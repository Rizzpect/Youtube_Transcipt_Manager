import os
import shutil

def get_title_from_file(file_path):
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        # Check for variations in the file format
        for line in lines:
            if line.startswith("Video URL:"):
                # Extract the title
                title = line.replace("Video URL:", "").strip()
                return title

        # If no suitable line is found, return None
        return None

def clean_filename(title):
    # Replace invalid characters with underscores
    invalid_chars = r'\/:*?"<>|'
    cleaned_title = ''.join(c if c not in invalid_chars else '_' for c in title)
    return cleaned_title

def rename_markdown_files(folder_path, renamed_folder, no_rename_folder):
    success_count = 0
    error_count = 0

    # Create the "RENAMED" and "NORENAMED" folders if they don't exist
    if not os.path.exists(renamed_folder):
        os.makedirs(renamed_folder)
    if not os.path.exists(no_rename_folder):
        os.makedirs(no_rename_folder)

    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)

            # Extract the title
            title = get_title_from_file(file_path)

            if title is not None:
                # Clean the title for valid filename
                cleaned_title = clean_filename(title)

                # Rename the file
                new_filename = f"{cleaned_title}.md"
                new_file_path = os.path.join(renamed_folder, new_filename)

                os.rename(file_path, new_file_path)
                print(f"Renamed: {filename} -> {new_filename}")
                success_count += 1
            else:
                # Move the file to the "NORENAMED" folder
                error_count += 1
                no_rename_path = os.path.join(no_rename_folder, filename)
                shutil.move(file_path, no_rename_path)
                print(f"Error: {filename} - Moved to {no_rename_path}")

    print("\nSummary:")
    print(f"Total files processed: {success_count + error_count}")
    print(f"Files renamed successfully: {success_count}")
    print(f"Files with errors: {error_count}")

if __name__ == "__main__":
    folder_path = r"D:\GITHUB\transcripts"
    renamed_folder = r"D:\GITHUB\transcripts\RENAMED"
    no_rename_folder = r"D:\GITHUB\transcripts\NORENAMED"

    rename_markdown_files(folder_path, renamed_folder, no_rename_folder)
