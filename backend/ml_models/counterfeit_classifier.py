"""
Counterfeit Classifier - Production Wrapper

Loads trained Random Forest model and provides prediction interface
for integration with main.py API
"""

import joblib
import numpy as np
from pathlib import Path
from feature_extractor import extract_features, features_to_vector


class CounterfeitClassifier:
    """
    Random Forest-based counterfeit detection classifier
    
    Combines:
    - Visual features (from YOLOv8)
    - Behavioral features (from supply chain analysis)
    - Database validation
    
    Predicts: AUTHENTIC or COUNTERFEIT with confidence score
    """
    
    def __init__(self):
        """Load trained models from disk"""
        
        model_dir = Path(__file__).parent.parent / 'trained_models'
        
        self.rf_path = model_dir / 'rf_classifier.pkl'
        self.scaler_path = model_dir / 'scaler.pkl'
        
        # Check if models exist
        if not self.rf_path.exists():
            raise FileNotFoundError(
                f"Random Forest model not found!\n"
                f"Expected: {self.rf_path}\n"
                f"Run: python train_random_forest.py"
            )
        
        if not self.scaler_path.exists():
            raise FileNotFoundError(
                f"Scaler not found!\n"
                f"Expected: {self.scaler_path}\n"
                f"Run: python train_random_forest.py"
            )
        
        # Load models
        print(f"📥 Loading Random Forest model...")
        self.model = joblib.load(self.rf_path)
        self.scaler = joblib.load(self.scaler_path)
        print(f"✅ Models loaded successfully!")
    
    def predict(self, drug_id, supply_chain, yolo_features=None):
        """
        Predict if drug is counterfeit
        
        Args:
            drug_id: Drug ID from database (integer)
            supply_chain: List of supply chain event dicts
            yolo_features: Optional dict from YOLOv8 detection
                          {'packaging_present': 0/1, 'packaging_confidence': 0.0-1.0}
        
        Returns:
            dict: {
                'is_counterfeit': bool,
                'confidence': float (0-1),
                'risk_level': str ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
                'verdict': str ('AUTHENTIC', 'COUNTERFEIT'),
                'features_used': dict,
                'explanation': str
            }
        """
        
        try:
            # Extract features
            features = extract_features(drug_id, supply_chain, yolo_features)
            feature_vector = features_to_vector(features)
            
            # Scale features
            feature_array = np.array(feature_vector).reshape(1, -1)
            feature_scaled = self.scaler.transform(feature_array)
            
            # Predict
            prediction = self.model.predict(feature_scaled)[0]
            probabilities = self.model.predict_proba(feature_scaled)[0]
            
            # Extract probabilities
            prob_authentic = float(probabilities[0])
            prob_counterfeit = float(probabilities[1])
            
            # Determine result
            is_counterfeit = bool(prediction)
            confidence = prob_counterfeit if is_counterfeit else prob_authentic
            
            # Risk level classification
            if confidence >= 0.9:
                risk_level = "CRITICAL"
            elif confidence >= 0.7:
                risk_level = "HIGH"
            elif confidence >= 0.5:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            # Generate explanation
            explanation = self._generate_explanation(features, is_counterfeit)
            
            return {
                'is_counterfeit': is_counterfeit,
                'confidence': confidence,
                'probability_authentic': prob_authentic,
                'probability_counterfeit': prob_counterfeit,
                'risk_level': risk_level,
                'verdict': 'COUNTERFEIT' if is_counterfeit else 'AUTHENTIC',
                'features_used': features,
                'explanation': explanation
            }
        
        except Exception as e:
            # Handle errors gracefully
            return {
                'is_counterfeit': None,
                'confidence': 0.0,
                'risk_level': 'UNKNOWN',
                'verdict': 'ERROR',
                'error': str(e)
            }
    
    def _generate_explanation(self, features, is_counterfeit):
        """
        Generate human-readable explanation of prediction
        
        Args:
            features: Feature dict
            is_counterfeit: Prediction result
        
        Returns:
            str: Explanation text
        """
        
        reasons = []
        
        # Check critical features
        if features['max_speed_kmh'] > 900:
            reasons.append(
                f"Impossible travel speed detected ({features['max_speed_kmh']:.0f} km/h). "
                f"Maximum feasible speed is ~900 km/h (airplane)."
            )
        
        if features['packaging_present'] == 0:
            reasons.append(
                f"No medicine packaging detected in image (confidence: {features['packaging_confidence']:.1%})."
            )
        elif features['packaging_confidence'] < 0.6:
            reasons.append(
                f"Low packaging detection confidence ({features['packaging_confidence']:.1%})."
            )
        
        if features['license_valid'] == 0:
            reasons.append("Manufacturing license is invalid or missing.")
        
        if features['price_valid'] == 0:
            reasons.append("Invalid MRP (Maximum Retail Price).")
        
        if features['location_deviation'] >= 2:
            reasons.append(
                f"Supply chain route deviation: {features['location_deviation']} "
                f"locations missing from expected path."
            )
        
        if features['total_locations'] <= 2:
            reasons.append(
                f"Insufficient supply chain checkpoints ({features['total_locations']}). "
                f"Expected at least 3-4 locations."
            )
        
        if features['recent_failures'] > 0:
            reasons.append(
                f"Fraud history: {features['recent_failures']} failed verification attempts "
                f"for this batch in the last 30 days."
            )
        
        if features['weekend_scan'] == 1:
            reasons.append("Suspicious: Scanned on weekend (unusual for pharmaceutical supply chain).")
        
        # Build explanation
        if is_counterfeit:
            if reasons:
                explanation = "COUNTERFEIT detected. Red flags: " + " ".join(reasons)
            else:
                explanation = "COUNTERFEIT detected. Multiple minor anomalies combined."
        else:
            explanation = "AUTHENTIC. All verification checks passed."
        
        return explanation
    
    def get_feature_importance(self):
        """
        Get feature importance from trained model
        
        Returns:
            dict: Feature names mapped to importance scores
        """
        
        from feature_extractor import FEATURE_NAMES
        
        importances = self.model.feature_importances_
        
        return {
            name: float(importance) 
            for name, importance in zip(FEATURE_NAMES, importances)
        }


# =============================================================================
# DEMO / TESTING
# =============================================================================

if __name__ == '__main__':
    print("="*70)
    print("🧪 COUNTERFEIT CLASSIFIER - DEMO")
    print("="*70)
    
    try:
        # Initialize classifier
        classifier = CounterfeitClassifier()
        
        print(f"\n📊 Feature Importance:")
        importances = classifier.get_feature_importance()
        sorted_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)
        
        for name, importance in sorted_features:
            bar = '█' * int(importance * 50)
            print(f"   {name:25s} {importance:.3f} {bar}")
        
        # Test Case 1: Authentic drug
        print(f"\n" + "="*70)
        print("📦 Test Case 1: AUTHENTIC DRUG")
        print("="*70)
        
        authentic_chain = [
            {
                'location': 'Factory',
                'latitude': 12.9716,
                'longitude': 77.5946,
                'timestamp': '2024-12-29 10:00:00'
            },
            {
                'location': 'Quality Check',
                'latitude': 12.9800,
                'longitude': 77.6000,
                'timestamp': '2024-12-29 14:00:00'
            },
            {
                'location': 'Warehouse',
                'latitude': 19.0760,
                'longitude': 72.8777,
                'timestamp': '2024-12-30 12:00:00'
            },
            {
                'location': 'Retail',
                'latitude': 28.7041,
                'longitude': 77.1025,
                'timestamp': '2024-12-31 15:00:00'
            }
        ]
        
        yolo_good = {
            'packaging_present': 1,
            'packaging_confidence': 0.95
        }
        
        result = classifier.predict(
            drug_id=1,
            supply_chain=authentic_chain,
            yolo_features=yolo_good
        )
        
        print(f"\n✅ Prediction Result:")
        print(f"   Verdict:     {result['verdict']}")
        print(f"   Confidence:  {result['confidence']:.2%}")
        print(f"   Risk Level:  {result['risk_level']}")
        print(f"\n   Probabilities:")
        print(f"   - Authentic:    {result['probability_authentic']:.2%}")
        print(f"   - Counterfeit:  {result['probability_counterfeit']:.2%}")
        print(f"\n   Explanation:")
        print(f"   {result['explanation']}")
        
        # Test Case 2: Counterfeit drug (cloned QR)
        print(f"\n" + "="*70)
        print("🚨 Test Case 2: COUNTERFEIT DRUG (Cloned QR)")
        print("="*70)
        
        fake_chain = [
            {
                'location': 'Mumbai',
                'latitude': 19.0760,
                'longitude': 72.8777,
                'timestamp': '2024-12-29 10:00:00'
            },
            {
                'location': 'Delhi',
                'latitude': 28.7041,
                'longitude': 77.1025,
                'timestamp': '2024-12-29 10:10:00'  # 10 minutes! Impossible!
            }
        ]
        
        yolo_suspicious = {
            'packaging_present': 0,
            'packaging_confidence': 0.35
        }
        
        result = classifier.predict(
            drug_id=999,  # Assume doesn't exist
            supply_chain=fake_chain,
            yolo_features=yolo_suspicious
        )
        
        print(f"\n❌ Prediction Result:")
        print(f"   Verdict:     {result['verdict']}")
        print(f"   Confidence:  {result['confidence']:.2%}")
        print(f"   Risk Level:  {result['risk_level']}")
        print(f"\n   Probabilities:")
        print(f"   - Authentic:    {result['probability_authentic']:.2%}")
        print(f"   - Counterfeit:  {result['probability_counterfeit']:.2%}")
        print(f"\n   Explanation:")
        print(f"   {result['explanation']}")
        
        # Test Case 3: Text-only verification (no image)
        print(f"\n" + "="*70)
        print("📱 Test Case 3: TEXT-ONLY VERIFICATION (No Image)")
        print("="*70)
        
        result = classifier.predict(
            drug_id=1,
            supply_chain=authentic_chain,
            yolo_features=None  # No image provided
        )
        
        print(f"\n✅ Prediction Result:")
        print(f"   Verdict:     {result['verdict']}")
        print(f"   Confidence:  {result['confidence']:.2%}")
        print(f"   Risk Level:  {result['risk_level']}")
        print(f"\n   Note: Without image, packaging features use default values")
        
        print(f"\n" + "="*70)
        print("✅ Counterfeit Classifier Demo Complete!")
        print("="*70)
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\nPlease run training first:")
        print(f"   1. python generate_training_data.py")
        print(f"   2. python train_random_forest.py")