import os

# The folder where your daily news files are stored
TARGET_FOLDER = '2026'

def clean_filenames():
    """Removes the 'GN-' prefix from all .md files in the target folder."""
    
    # Verify the folder actually exists before trying to run
    if not os.path.exists(TARGET_FOLDER):
        print(f"[ERROR] Could not find the folder: {TARGET_FOLDER}/")
        print("Make sure this script is in the root of your TGCA repository.")
        return

    print(f"Scanning the {TARGET_FOLDER}/ directory...\n")
    renamed_count = 0

    # Look at every file inside the 2026 folder
    for filename in os.listdir(TARGET_FOLDER):
        
        # We only want to touch files that match our exact old format
        if filename.startswith("GN-") and filename.endswith(".md"):
            
            # Slice off the first 3 characters ("GN-") to get the clean date
            new_filename = filename[3:]
            
            # Construct the full file paths needed by the operating system
            old_file_path = os.path.join(TARGET_FOLDER, filename)
            new_file_path = os.path.join(TARGET_FOLDER, new_filename)
            
            # Execute the rename
            os.rename(old_file_path, new_file_path)
            
            print(f"Changed: {filename}  ->  {new_filename}")
            renamed_count += 1

    print(f"\n[SUCCESS] Pipeline complete. Cleaned up {renamed_count} files.")

if __name__ == "__main__":
    clean_filenames()
