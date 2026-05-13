"""
MediTrace Celery Worker — The Heavy Lifter
==========================================
ML models are loaded ONCE at worker boot (global scope).
FastAPI never touches Ultralytics or Scikit-learn.

Edge Case Defenses:
  1. Race Condition:  FastAPI generates UUID4-prefixed filenames before dispatch.
  2. Zombie Files:    os.remove() lives in `finally` — executes even on OOM/tensor crash.
  3. Cold Start Tax:  Models instantiated globally, NOT inside the task function.
"""

import os
import sys
import cv2
import numpy as np
import traceback
from pathlib import Path

from celery_app import celery
from database import SessionLocal
import crud

# ═══════════════════════════════════════════════════
# GLOBAL MODEL INSTANTIATION (loaded once at worker boot)
# ═══════════════════════════════════════════════════

# Add ml_models to Python path so imports resolve
ml_models_path = Path(__file__).parent / "ml_models"
sys.path.insert(0, str(ml_models_path))

yolo_detector = None
rf_classifier = None

try:
    from yolo_detector import PackagingDetector
    from counterfeit_classifier import CounterfeitClassifier

    print("🤖 [WORKER] Loading ML models into worker process...")
    yolo_detector = PackagingDetector()
    rf_classifier = CounterfeitClassifier()
    print("✅ [WORKER] ML models loaded. Worker ready for inference.")
except Exception as e:
    print(f"💀 [WORKER] FATAL: ML models failed to load: {e}")
    print("   A worker without models is a zombie. Shutting down.")
    sys.exit(1)


# ═══════════════════════════════════════════════════
# CELERY TASK: process_verification
# ═══════════════════════════════════════════════════

@celery.task(name="process_verification", bind=True, max_retries=1)
def process_verification(self, file_path: str, unique_id: str, task_id: str):
    """
    Run YOLO + Random Forest inference on an uploaded image.

    This task is dispatched by FastAPI's /verify-image endpoint.
    It spins up its own database session (cannot use FastAPI's Depends).

    Args:
        file_path: Absolute path to the temp image file (UUID-prefixed).
        unique_id: The drug's unique_id extracted from the QR code.
        task_id: The UUID4 task identifier returned to the client.

    Returns:
        dict: Verification result (status, ml_analysis, visual_verification, etc.)
    """
    db = SessionLocal()

    try:
        # ── Step 1: Read image from disk ──────────────────────
        if not os.path.exists(file_path):
            return {
                "task_id": task_id,
                "status": "error",
                "message": f"Image file not found at {file_path}"
            }

        img = cv2.imread(file_path)
        if img is None:
            return {
                "task_id": task_id,
                "status": "error",
                "message": "Image file is corrupted or unreadable"
            }

        # ── Step 2: YOLO Detection ────────────────────────────
        yolo_result = None
        if yolo_detector:
            try:
                yolo_result = yolo_detector.detect(image_array=img)
                print(
                    f"📦 [WORKER] YOLO: Packaging "
                    f"{'detected' if yolo_result['packaging_present'] else 'NOT detected'} "
                    f"(confidence: {yolo_result['packaging_confidence']:.2%})"
                )
            except Exception as e:
                print(f"⚠️  [WORKER] YOLO detection failed: {e}")
                yolo_result = None

        # ── Step 3: Database lookup ───────────────────────────
        drug = crud.get_drug_by_unique_id(db, unique_id)
        if not drug:
            crud.log_failed_attempt(
                db=db,
                scanned_id=unique_id,
                attempt_type="FAKE_QR_IMAGE",
                reason=f"Worker task - QR decoded to '{unique_id}' but not in database"
            )
            return {
                "task_id": task_id,
                "status": "fake",
                "message": f"Invalid QR Code: {unique_id}"
            }

        # ── Step 4: Get supply chain ──────────────────────────
        supply_chain = crud.get_supply_chain(db, drug.id)

        # ── Step 5: Random Forest Prediction ──────────────────
        ml_prediction = None
        if rf_classifier:
            try:
                yolo_features = None
                if yolo_result:
                    yolo_features = {
                        "packaging_present": 1 if yolo_result["packaging_present"] else 0,
                        "packaging_confidence": yolo_result["packaging_confidence"],
                    }

                ml_prediction = rf_classifier.predict(
                    drug_id=drug.id,
                    supply_chain=supply_chain,
                    yolo_features=yolo_features,
                    db_session=db
                )
                print(
                    f"🌳 [WORKER] Random Forest: {ml_prediction['verdict']} "
                    f"(confidence: {ml_prediction['confidence']:.2%})"
                )

                # If counterfeit with high confidence, log it
                if ml_prediction["is_counterfeit"] and ml_prediction["confidence"] > 0.75:
                    crud.log_failed_attempt(
                        db=db,
                        scanned_id=unique_id,
                        attempt_type="ML_COUNTERFEIT_DETECTED",
                        reason=f"Visual + Behavioral analysis: {ml_prediction['explanation']}",
                    )
                    return {
                        "task_id": task_id,
                        "status": "suspicious",
                        "message": "⚠️ COUNTERFEIT DETECTED (ML Analysis)",
                        "unique_id": unique_id,
                        "name": drug.drug_name,
                        "batchId": drug.batch_id,
                        "ml_analysis": {
                            "verdict": ml_prediction["verdict"],
                            "confidence": f"{ml_prediction['confidence']:.1%}",
                            "risk_level": ml_prediction["risk_level"],
                            "explanation": ml_prediction["explanation"],
                            "visual_check": {
                                "packaging_detected": yolo_result["packaging_present"] if yolo_result else None,
                                "confidence": f"{yolo_result['packaging_confidence']:.1%}" if yolo_result else None,
                            },
                        },
                    }
            except Exception as e:
                print(f"⚠️  [WORKER] ML prediction failed: {e}")
                traceback.print_exc()
                ml_prediction = None

        # ── Step 6: Build response ────────────────────────────
        locations = []
        for event in supply_chain:
            timestamp = str(event.timestamp)
            date_part = timestamp.split(" ")[0] if " " in timestamp else timestamp
            time_part = timestamp.split(" ")[1] if " " in timestamp else "00:00:00"
            locations.append({
                "place": event.location,
                "date": date_part,
                "time": time_part,
                "lat": event.latitude,
                "lon": event.longitude,
                "status": "verified",
            })

        result = {
            "task_id": task_id,
            "status": "authentic",
            "unique_id": unique_id,
            "name": drug.drug_name,
            "genericName": drug.generic_name,
            "batchId": drug.batch_id,
            "manufacturer": drug.manufacturer,
            "dosage": drug.dosage,
            "hash": drug.hash,
            "mfgDate": str(drug.mfg_date),
            "expDate": str(drug.exp_date),
            "locations": locations,
        }

        # Attach YOLO results
        if yolo_result:
            result["visual_verification"] = {
                "packaging_detected": yolo_result["packaging_present"],
                "confidence": f"{yolo_result['packaging_confidence']:.2%}",
                "num_packages": yolo_result["num_packages"],
            }

        # Attach RF prediction
        if ml_prediction:
            result["ml_analysis"] = {
                "verdict": ml_prediction["verdict"],
                "confidence": f"{ml_prediction['confidence']:.1%}",
                "risk_level": ml_prediction["risk_level"],
                "probability_authentic": f"{ml_prediction['probability_authentic']:.1%}",
                "probability_counterfeit": f"{ml_prediction['probability_counterfeit']:.1%}",
            }

        return result

    except Exception as e:
        # ── Transient failure: let Celery retry before giving up ──
        print(f"❌ [WORKER] Task {task_id} crashed (attempt {self.request.retries + 1}): {e}")
        traceback.print_exc()

        try:
            # Retry with exponential backoff (5s, then 20s)
            raise self.retry(exc=e, countdown=5 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            # Retries exhausted — write permanent failure to DB
            print(f"💀 [WORKER] Task {task_id} permanently failed after {self.request.retries + 1} attempts.")
            try:
                crud.log_failed_attempt(
                    db=db,
                    scanned_id=unique_id,
                    attempt_type="WORKER_CRASH",
                    reason=f"Permanent failure after retries: {str(e)[:200]}",
                )
            except Exception:
                pass  # Don't let logging mask the original error

            return {
                "task_id": task_id,
                "status": "error",
                "message": "Verification failed after multiple attempts. Please retry later.",
            }

    finally:
        # ── MANDATORY CLEANUP — runs even on OOM/tensor crash ─
        db.close()

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️  [WORKER] Cleaned up temp file: {file_path}")
            except OSError as e:
                print(f"⚠️  [WORKER] Failed to delete temp file {file_path}: {e}")
