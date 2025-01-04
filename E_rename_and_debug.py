""""
This script renames files in a specified folder by extracting the part of the file name before 'https'.
It removes any trailing or leading hyphens and underscores, and appends the '.md' extension. 
Files that cannot be renamed (due to permission errors or invalid names) are moved to a 'NO RENAME' folder.
"""
""""""

import os
import shutil

def rename_files(folder_path):
    # Create a folder for files that couldn't be renamed
    no_rename_folder = os.path.join(folder_path, 'NO RENAME')
    os.makedirs(no_rename_folder, exist_ok=True)

    # List all files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Iterate through each file
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)

        # Extract the new file name by removing anything after 'https'
        new_file_name = file_name.split('https')[0].strip('-_ ') + '.md'  # Also remove leading/trailing - and _ and add .md

        # Ensure the new file name is not empty
        if new_file_name:
            new_file_path = os.path.join(folder_path, new_file_name)

            # Rename the file
            try:
                os.rename(file_path, new_file_path)
                print(f"Renamed: {file_name} -> {new_file_name}")
            except PermissionError:
                # If permission error, move to NO RENAME folder
                print(f"Permission error: {file_name}")
                shutil.move(file_path, os.path.join(no_rename_folder, f'#{file_name}'))
        else:
            # If the new file name is empty, move to NO RENAME folder
            print(f"Empty new file name: {file_name}")
            shutil.move(file_path, os.path.join(no_rename_folder, f'#{file_name}'))

if __name__ == "__main__":
    folder_path = r'D:\GITHUB\transcripts\RENAMED' # folder path
    rename_files(folder_path)
