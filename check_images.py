import os
from PIL import Image

folder_path = "/path/to/pictures"
print("Checking folder contents...")

# Walk through all folders and subfolders
for root, dirs, files in os.walk(folder_path):
    for filename in files:
        if filename.lower().endswith(".png"):  # Case-insensitive check for .png files
            image_path = os.path.join(root, filename)
            try:
                with Image.open(image_path) as img:
                    img.verify()  # Check if it's an actual image without loading
                pass
            except (IOError, Image.UnidentifiedImageError):
                print(f"{filename} in folder {root} is corrupted or cannot be identified.")
