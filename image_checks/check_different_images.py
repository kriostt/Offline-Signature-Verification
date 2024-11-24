import os
from collections import defaultdict

def find_similar_files(root_folder):
    """
    This function recursively checks for files with similar names within a folder structure.
    
    Args:
        root_folder (str): Path to the root folder where the search begins.
    
    Returns:
        dict: A dictionary containing similar file names and their paths.
    """
    file_names = defaultdict(list)  # To store files with similar names
    similar_files = defaultdict(list)  # To store actual similar file names

    # Walk through all files in the directory structure
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            file_name = file.lower()  # Compare case-insensitive file names
            file_path = os.path.join(root, file)
            file_names[file_name].append(file_path)

    # Check for files with the same name in different locations
    for name, paths in file_names.items():
        if len(paths) > 1:  # More than one file with the same name
            similar_files[name] = paths

    return similar_files

# Example usage
if __name__ == "__main__":
    root_folder = "C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset4"
    if os.path.exists(root_folder) and os.path.isdir(root_folder):
        similar_files = find_similar_files(root_folder)
        if similar_files:
            print("\nSimilar Files Found:")
            for name, paths in similar_files.items():
                print(f"\n{name}:")
                for path in paths:
                    print(f"  - {path}")
        else:
            print("No similar file names found.")
    else:
        print(f"The path '{root_folder}' is invalid or not a folder.")
