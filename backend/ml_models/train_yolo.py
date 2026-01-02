"""
YOLOv8 Training Script for MediTrace Packaging Detection
"""

from ultralytics import YOLO
import torch
from pathlib import Path
import time

def train_yolov8():
    """Train YOLOv8 model on medicine packaging dataset"""
    
    print("="*70)
    print("🚀 MEDITRACE - YOLOV8 TRAINING")
    print("="*70)
    
    # Check device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\n💻 Device: {device}")
    
    if device == 'cpu':
        print("⚠️  Training on CPU - This will take 1-2 hours")
        print("   Tip: Use Google Colab for GPU training (15-20 mins)")
    else:
        print("✅ GPU detected! Training will be fast (~15-20 mins)")
    
    # Check dataset
    data_yaml = Path('../dataset/data.yaml')
    if not data_yaml.exists():
        print(f"\n❌ ERROR: data.yaml not found at {data_yaml.absolute()}")
        return
    
    print(f"\n📊 Dataset config: {data_yaml.absolute()}")
    
    # Load pre-trained YOLOv8-nano model
    print(f"\n📥 Loading YOLOv8-nano pre-trained model...")
    model = YOLO('yolov8n.pt')
    
    print(f"✅ Model loaded: YOLOv8-nano (3.2M parameters)")
    
    # Training parameters
    config = {
        'data': str(data_yaml),
        'epochs': 50,
        'imgsz': 640,
        'batch': 16,
        'device': device,
        'patience': 15,
        'save': True,
        'plots': True,
        'val': True,
        'hsv_h': 0.015,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 10,
        'translate': 0.1,
        'scale': 0.5,
        'fliplr': 0.5,
        'mosaic': 1.0,
        'optimizer': 'AdamW',
        'lr0': 0.001,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'project': 'runs/train',
        'name': 'meditrace_packaging',
        'exist_ok': True
    }
    
    print(f"\n⚙️  Training Configuration:")
    print(f"   Epochs: {config['epochs']}")
    print(f"   Batch Size: {config['batch']}")
    print(f"   Image Size: {config['imgsz']}x{config['imgsz']}")
    print(f"   Device: {config['device']}")
    
    print(f"\n🏋️  Starting training...")
    print(f"   Estimated time: {'1-2 hours' if device == 'cpu' else '15-20 mins'}")
    print("\n" + "="*70)
    
    start_time = time.time()
    
    try:
        results = model.train(**config)
        
        elapsed = time.time() - start_time
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETED!")
        print("="*70)
        
        print(f"\n⏱️  Training time: {elapsed//60:.0f} minutes {elapsed%60:.0f} seconds")
        
        # Save best model
        best_model = Path('runs/train/meditrace_packaging/weights/best.pt')
        target = Path('../trained_models/yolov8_packaging.pt')
        target.parent.mkdir(exist_ok=True)
        
        if best_model.exists():
            import shutil
            shutil.copy(best_model, target)
            print(f"\n💾 Best model saved to: {target}")
        
        print(f"\n📈 Training plots saved to:")
        print(f"   runs/train/meditrace_packaging/")
        
        return str(target)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        return None
    
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏥 MEDITRACE - YOLOV8 PACKAGING DETECTION")
    print("="*70)
    
    model_path = train_yolov8()
    
    if model_path:
        print("\n" + "="*70)
        print("🎉 TRAINING COMPLETE! MODEL READY!")
        print("="*70)
        print(f"\n📋 Model saved at: {model_path}")
        print(f"📊 Check plots: runs/train/meditrace_packaging/")