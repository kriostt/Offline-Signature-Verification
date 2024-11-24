import os

def count_files_in_subfolders(folder_path):
    """
    Counts the number of files in each immediate subfolder of a given folder.
    
    Args:
        folder_path (str): The path to the root folder.
    
    Returns:
        dict: A dictionary where keys are subfolder paths and values are the number of files in them.
    """
    folder_file_counts = {}

    for subfolder_name in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder_name)

        # Ensure it's a directory
        if os.path.isdir(subfolder_path):
            # Count all files in this subfolder (including nested ones)
            file_count = 0
            for root, _, files in os.walk(subfolder_path):
                file_count += len(files)
            folder_file_counts[subfolder_path] = file_count

    return folder_file_counts

# Example usage
if __name__ == "__main__":
    folder_path = "C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset4/test - database signatures/forged"
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        results = count_files_in_subfolders(folder_path)
        print("\nFile Counts in Subfolders:")
        for subfolder, count in results.items():
            print(f"{subfolder}: {count} files")
    else:
        print(f"The path '{folder_path}' is invalid or not a folder.")
