# You need to have Pillow (PIL) installed: pip install Pillow
from PIL import Image
import os

# Paths to the images
images_to_resize = [
    "assets/app_icons/raspberry2.png"
]

for img_path in images_to_resize:
    if os.path.exists(img_path):
        with Image.open(img_path) as img:
            resized = img.resize((32, 32), Image.LANCZOS)
            resized.save(img_path)
        print(f"Resized {img_path} to 32×32.")
    else:
        print(f"File not found: {img_path}")