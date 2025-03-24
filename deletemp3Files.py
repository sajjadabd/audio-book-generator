import os

# Get the current directory
current_folder = os.getcwd()

# Iterate over files in the current folder
deleted_files = 0
for filename in os.listdir(current_folder):
    # Check if the file ends with .mp3
    if filename.endswith(".mp3"):
        file_path = os.path.join(current_folder, filename)
        try:
            os.remove(file_path)
            deleted_files += 1
            print(f"Deleted: {filename}")
        except Exception as e:
            print(f"Failed to delete {filename}: {e}")

if deleted_files == 0:
    print("No .mp3 files found.")
else:
    print(f"Successfully deleted {deleted_files} .mp3 file(s).")