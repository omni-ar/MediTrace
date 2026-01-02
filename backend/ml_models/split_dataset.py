"""
Split dataset into train/valid since Roboflow put everything in train
Splits 147 images into 80% train (118) and 20% valid (29)
"""

import os
import shutil
from pathlib import Path
import random

def split_dataset():
    """Split 147 training images into 118 train + 29 valid"""
    
    print("="*60)
    print("📊 SPLITTING DATASET")
    print("="*60)
    
    # Paths
    train_img = Path('../dataset/train/images')
    train_lbl = Path('../dataset/train/labels')
    
    valid_img = Path('../dataset/valid/images')
    valid_lbl = Path('../dataset/valid/labels')
    
    # Create valid directories
    valid_img.mkdir(parents=True, exist_ok=True)
    valid_lbl.mkdir(parents=True, exist_ok=True)
    
    print(f"\n✅ Created validation directories")
    
    # Get all training images
    all_images = sorted(train_img.glob('*.jpg')) + sorted(train_img.glob('*.JPG'))

    # Remove duplicates that can occur on case-insensitive filesystems
    seen = set()
    unique_images = []
    for p in all_images:
        if p.name not in seen:
            seen.add(p.name)
            unique_images.append(p)
    all_images = unique_images
    
    print(f"\n📁 Found {len(all_images)} training images (unique)")
    
    if len(all_images) == 0:
        print("❌ ERROR: No images found in train/images/")
        print(f"   Check path: {train_img.absolute()}")
        return
    
    # Calculate split (20% for validation)
    num_valid = int(len(all_images) * 0.2)
    
    print(f"\n🔀 Splitting:")
    print(f"   Validation: {num_valid} images (20%)")
    print(f"   Training:   {len(all_images) - num_valid} images (80%)")
    
    # Randomly select validation images
    random.seed(42)
    valid_images = random.sample(all_images, num_valid)
    
    print(f"\n📦 Moving {num_valid} images to validation set...")
    
    # Move to validation
    moved = 0
    for img_path in valid_images:
        # Some files may have been listed twice or already moved; check existence
        if not img_path.exists():
            print(f"   ⚠️  Warning: Source image not found (skipping) {img_path.name}")
            continue
        try:
            # Move image
            shutil.move(str(img_path), str(valid_img / img_path.name))
            
            # Move corresponding label
            label_name = img_path.stem + '.txt'
            label_path = train_lbl / label_name
            
            if label_path.exists():
                shutil.move(str(label_path), str(valid_lbl / label_name))
            else:
                print(f"   ⚠️  Warning: Label not found for {img_path.name}")
            
            moved += 1
            if moved % 10 == 0:
                print(f"   Moved {moved}/{num_valid}...")
        
        except Exception as e:
            print(f"   ❌ Error moving {img_path.name}: {e}")
    
    print(f"\n✅ Split complete!")
    
    # Verify
    train_count = len(list(train_img.glob('*.jpg'))) + len(list(train_img.glob('*.JPG')))
    valid_count = len(list(valid_img.glob('*.jpg'))) + len(list(valid_img.glob('*.JPG')))
    
    train_lbl_count = len(list(train_lbl.glob('*.txt')))
    valid_lbl_count = len(list(valid_lbl.glob('*.txt')))
    
    print(f"\n📊 Final counts:")
    print(f"   Training images:   {train_count}")
    print(f"   Training labels:   {train_lbl_count}")
    print(f"   Validation images: {valid_count}")
    print(f"   Validation labels: {valid_lbl_count}")
    print(f"   Total:             {train_count + valid_count} images")
    
    if train_count != train_lbl_count:
        print(f"\n⚠️  WARNING: Image/label count mismatch in training set!")
    
    if valid_count != valid_lbl_count:
        print(f"⚠️  WARNING: Image/label count mismatch in validation set!")
    
    print(f"\n✅ Dataset ready for training!")

if __name__ == '__main__':
    split_dataset()