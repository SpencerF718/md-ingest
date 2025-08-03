import os

MARKDOWN_EXTENSION = ".md"
DEFAULT_OUTPUT_FILENAME = "md_ingest.txt"


def get_vault_path():

    vault_found = False
    vault_path = ""

    while not vault_found:
        vault_path = input(
            r"Please enter the absolute path to your Obsidian vault. e.g. C:\Users\Name\Documents\Main")

        if os.path.isabs(vault_path):
            vault_found = True
        else:
            print("ERROR: Invalid path.")

    return vault_path


def get_output_path():

    output_found = False
    output_path = ""

    while not output_found:
        output_path = input(
            r"Please enter the absolute path to your output directory.  e.g. C:\Users\Name\Documents\Output")

        if os.path.isabs(output_path):
            try:
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                    output_found = True
            except OSError as e:
                print(
                    f"ERROR: Could not create directory {output_path}.  Because: {e}")
        else:
            print(f"ERROR: Invalid path.")

    return output_path


def get_file_names(vault_root_directory):

    markdown_files = []

    for current_directory, subdirectories, files in os.walk(vault_root_directory):
        for file_name in files:
            if file_name.endswith(MARKDOWN_EXTENSION):
                full_file_path = os.path.join(current_directory, file_name)
                markdown_files.append(full_file_path)

    return markdown_files


def main():

    vault_path = get_vault_path()
    output_path = get_output_path()

    resolved_vault_path = os.path.abspath(os.path.expanduser(vault_path))
    resolved_output_path = os.path.abspath(os.path.expanduser(output_path))

    final_combined_notes_file = os.path.join(
        resolved_output_path, DEFAULT_OUTPUT_FILENAME)

    print(f"\nVault Path: {resolved_vault_path}")
    print(f"Output Directory: {resolved_output_path}")
    print(f"Combined notes will be saved to: {final_combined_notes_file}")


if __name__ == "__main__":
    main()
