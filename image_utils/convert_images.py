import os
from PIL import Image

def convert_tiff_to_png(input_folder, output_folder):
    """
    Converts all TIFF files in a folder (and its subfolders) to PNG files,
    preserving the directory structure.
    
    Args:
        input_folder (str): Path to the folder containing TIFF files.
        output_folder (str): Path to the folder where the PNG files will be saved.
    """
    # Loop through all files and directories in the input folder
    for root, _, files in os.walk(input_folder):
        for filename in files:
            if filename.lower().endswith('.tif') or filename.lower().endswith('.tiff'):
                tiff_path = os.path.join(root, filename)
                
                # Construct the corresponding output folder path
                relative_path = os.path.relpath(root, input_folder)
                output_subfolder = os.path.join(output_folder, relative_path)
                os.makedirs(output_subfolder, exist_ok=True)

                # Define the output PNG file path
                png_filename = f"{os.path.splitext(filename)[0]}.png"
                png_path = os.path.join(output_subfolder, png_filename)

                try:
                    # Open the TIFF image and save as PNG
                    with Image.open(tiff_path) as img:
                        img.save(png_path, 'PNG')
                    print(f"Converted {filename} to {png_filename}")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

# Example usage
input_folder = "C:/Users/krisa/Desktop/CPRO 2902/signature_dataset3/BHSig260-Hindi/BHSig260-Hindi"
output_folder = "C:/Users/krisa/Desktop/CPRO 2902/signature_dataset3_png/Hindi"
convert_tiff_to_png(input_folder, output_folder)
