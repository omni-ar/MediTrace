"""
YOLOv8 Detector Wrapper for Medicine Packaging Detection

Provides simple interface for detecting medicine packaging in images
"""

from ultralytics import YOLO
from pathlib import Path
import numpy as np
import cv2


class PackagingDetector:
    """
    YOLOv8-based medicine packaging detector
    
    Detects presence and location of medicine packaging in images
    """
    
    def __init__(self):
        """Load trained YOLOv8 model"""
        
        model_path = Path(__file__).parent.parent / 'trained_models' / 'yolov8_packaging.pt'
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"YOLOv8 model not found!\n"
                f"Expected: {model_path}\n"
                f"Please ensure model is trained and saved."
            )
        
        print(f"📥 Loading YOLOv8 packaging detector...")
        self.model = YOLO(str(model_path))
        print(f"✅ YOLOv8 model loaded successfully!")
    
    def detect(self, image_path=None, image_array=None):
        """
        Detect medicine packaging in image
        
        Args:
            image_path: Path to image file (str or Path)
            image_array: numpy array (H, W, 3) - RGB or BGR
        
        Returns:
            dict: {
                'packaging_present': bool,
                'packaging_confidence': float (0-1),
                'num_packages': int,
                'bounding_boxes': list of [x1, y1, x2, y2],
                'confidences': list of floats
            }
        """
        
        try:
            # Run inference
            if image_path:
                results = self.model(image_path, verbose=False)
            elif image_array is not None:
                results = self.model(image_array, verbose=False)
            else:
                raise ValueError("Must provide either image_path or image_array")
            
            # Parse results
            result = results[0]
            boxes = result.boxes
            
            if len(boxes) == 0:
                # No packaging detected
                return {
                    'packaging_present': False,
                    'packaging_confidence': 0.0,
                    'num_packages': 0,
                    'bounding_boxes': [],
                    'confidences': []
                }
            
            # Extract detections
            confidences = [float(box.conf[0]) for box in boxes]
            bboxes = [box.xyxy[0].tolist() for box in boxes]
            
            # Get highest confidence detection
            max_confidence = max(confidences)
            
            # Packaging present if confidence > 50%
            packaging_present = max_confidence > 0.5
            
            return {
                'packaging_present': packaging_present,
                'packaging_confidence': max_confidence,
                'num_packages': len(boxes),
                'bounding_boxes': bboxes,
                'confidences': confidences
            }
        
        except Exception as e:
            print(f"❌ Error in YOLOv8 detection: {e}")
            return {
                'packaging_present': False,
                'packaging_confidence': 0.0,
                'num_packages': 0,
                'bounding_boxes': [],
                'confidences': [],
                'error': str(e)
            }
    
    def detect_from_bytes(self, image_bytes):
        """
        Detect from image bytes (useful for API uploads)
        
        Args:
            image_bytes: bytes object
        
        Returns:
            dict: Same as detect()
        """
        
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Run detection
            return self.detect(image_array=img)
        
        except Exception as e:
            print(f"❌ Error decoding image: {e}")
            return {
                'packaging_present': False,
                'packaging_confidence': 0.0,
                'num_packages': 0,
                'error': str(e)
            }


# =============================================================================
# DEMO / TESTING
# =============================================================================

if __name__ == '__main__':
    print("="*70)
    print("🧪 YOLO PACKAGING DETECTOR - DEMO")
    print("="*70)
    
    try:
        # Initialize detector
        detector = PackagingDetector()
        
        # Test on a validation image
        test_image = Path(__file__).parent.parent / 'dataset' / 'valid' / 'images'
        images = list(test_image.glob('*.jpg')) + list(test_image.glob('*.JPG'))
        
        if not images:
            print("\n⚠️  No test images found in dataset/valid/images/")
            print("   Run this demo after training YOLOv8.")
        else:
            print(f"\n📸 Testing on: {images[0].name}")
            
            result = detector.detect(str(images[0]))
            
            print(f"\n✅ Detection Result:")
            print(f"   Packaging Present:  {result['packaging_present']}")
            print(f"   Confidence:         {result['packaging_confidence']:.2%}")
            print(f"   Num Packages:       {result['num_packages']}")
            
            if result['num_packages'] > 0:
                print(f"\n   Bounding Boxes:")
                for i, (bbox, conf) in enumerate(zip(result['bounding_boxes'], result['confidences'])):
                    print(f"     Box {i+1}: {bbox} (confidence: {conf:.2%})")
        
        print(f"\n" + "="*70)
        print("✅ YOLOv8 Detector Demo Complete!")
        print("="*70)
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\nPlease ensure YOLOv8 model is trained:")
        print(f"   1. python train_yolo.py")
        print(f"   2. Check trained_models/yolov8_packaging.pt exists")