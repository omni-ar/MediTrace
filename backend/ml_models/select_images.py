"""
Smart image selection from Kaggle dataset
Selects diverse, high-quality images
Works with nested folder structure from Kaggle
"""

import os
import shutil
from pathlib import Path
import random
from PIL import Image

def select_best_images(
    source_dir='../dataset/raw',
    target_dir='../dataset/selected',
    num_images=50
):
    """
    Select best images from nested Kaggle dataset structure
    
    Searches recursively through all subfolders
    """
    
    print("🔍 Scanning images (checking subfolders)...")
    
    source = Path(source_dir)
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    
    # Get all image files RECURSIVELY (searches subfolders too!)
    all_images = []
    all_images.extend(list(source.rglob('*.jpg')))   # .rglob = recursive glob
    all_images.extend(list(source.rglob('*.JPG')))
    all_images.extend(list(source.rglob('*.png')))
    all_images.extend(list(source.rglob('*.PNG')))
    all_images.extend(list(source.rglob('*.jpeg')))
    all_images.extend(list(source.rglob('*.JPEG')))
    
    print(f"📊 Found {len(all_images)} total images across all folders")
    
    if len(all_images) == 0:
        print("\n❌ ERROR: No images found!")
        print("📁 Check your folder structure:")
        print(f"   Looking in: {source.absolute()}")
        print("\n💡 Tips:")
        print("   1. Make sure images are extracted")
        print("   2. Check if there's a nested folder inside raw/")
        print("   3. Try: ls ../dataset/raw/")
        return 0
    
    # Show some examples of found images
    print("\n📸 Sample images found:")
    for img in all_images[:5]:
        print(f"   - {img.name} (in {img.parent.name}/)")
    
    # Filter by quality
    good_images = []
    corrupted_count = 0
    small_count = 0
    
    print("\n🔍 Checking image quality...")
    
    for img_path in all_images:
        try:
            # Open image to check if valid
            img = Image.open(img_path)
            width, height = img.size
            
            # Keep only good resolution images
            if width >= 400 and height >= 400:
                good_images.append(img_path)
            else:
                small_count += 1
            
        except Exception as e:
            # Skip corrupted images
            corrupted_count += 1
            continue
    
    print(f"✅ Found {len(good_images)} good quality images")
    print(f"⚠️  Skipped {small_count} small images (< 400x400)")
    print(f"⚠️  Skipped {corrupted_count} corrupted images")
    
    # Randomly select 50
    if len(good_images) > num_images:
        selected = random.sample(good_images, num_images)
    else:
        selected = good_images
        print(f"ℹ️  Only {len(selected)} images available (less than {num_images})")
    
    print(f"\n🎯 Selected {len(selected)} images for labeling")
    
    # Copy to target folder
    print("\n📦 Copying images...")
    for i, img_path in enumerate(selected, 1):
        # Rename with sequential numbers for easy tracking
        # Keep original extension
        new_name = f"medicine_{i:03d}{img_path.suffix}"
        target_path = target / new_name
        
        shutil.copy(img_path, target_path)
        
        if i % 10 == 0:
            print(f"   Copied {i}/{len(selected)}...")
    
    print(f"\n✅ Done! Selected images saved to: {target.absolute()}")
    print(f"📁 Next step: Label these {len(selected)} images on Roboflow")
    
    return len(selected)


if __name__ == '__main__':
    print("="*60)
    print("🏥 MEDITRACE - IMAGE SELECTION TOOL")
    print("="*60)
    
    # Run selection
    count = select_best_images(num_images=50)
    
    if count > 0:
        print("\n" + "="*60)
        print("🎉 SELECTION COMPLETE!")
        print("="*60)
        print(f"📊 You now have {count} manageable images to label")
        print(f"⏰ Estimated labeling time: {count * 2} minutes (~{count * 2 // 60} hours)")
        print("\n📋 Next Steps:")
        print("   1. Go to: https://roboflow.com")
        print("   2. Create project: 'MediTrace Packaging'")
        print("   3. Upload images from: backend/dataset/selected/")
        print("   4. Label 3 classes: hologram, seal, label")
        print("   5. Generate dataset with augmentation")
        print("   6. Export as YOLOv8 format")
    else:
        print("\n❌ FAILED - No images selected")
        print("\n🔧 TROUBLESHOOTING:")
        print("   Try this command to see what's in raw folder:")
        print("   ls -la ../dataset/raw/")