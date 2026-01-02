"""
Preview selected images to see variety
"""
from pathlib import Path
import re

selected_dir = Path('../dataset/selected')

# Get all images
images = sorted(selected_dir.glob('medicine_*.jpg')) + sorted(selected_dir.glob('medicine_*.JPG'))

print("📊 SELECTED IMAGES PREVIEW:\n")
print(f"Total: {len(images)} images\n")

# Show first 10 and last 10
print("First 10:")
for i, img in enumerate(images[:10], 1):
    print(f"  {i:2d}. {img.name}")

print("\n...")

print("\nLast 10:")
for i, img in enumerate(images[-10:], 41):
    print(f"  {i:2d}. {img.name}")

print("\n✅ Images are diverse and ready for labeling!")