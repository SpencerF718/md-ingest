import os
import re

MARKDOWN_EXTENSION = ".md"
DEFAULT_OUTPUT_FILENAME = "md_ingest.txt"

FILE_SEPARATOR = "\n\n" + "=" * 80 + "\n\n"
FILE_HEADER_PREFIX = "FILE: "


def get_vault_path():
    vault_found = False
    vault_path = ""

    while not vault_found:
        vault_path = input(
            r"Please enter the absolute path to your Obsidian vault. (e.g. C:\Users\Name\Documents\Main): "
        )

        if os.path.isabs(vault_path) and os.path.isdir(vault_path):
            vault_found = True
        else:
            print(
                "ERROR: Invalid or non-existent directory. Please enter a valid absolute path."
            )
    return vault_path


def get_output_path():
    output_found = False
    output_path = ""

    while not output_found:
        output_path = input(
            r"Please enter the absolute path to your output directory. (e.g. C:\Users\Name\Documents\Output): "
        )

        if os.path.isabs(output_path):
            try:
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                output_found = True
            except OSError as e:
                print(
                    f"ERROR: Could not create directory {output_path}. Because: {e}")
        else:
            print("ERROR: Invalid path.")
    return output_path


def get_file_names(vault_root_directory):
    markdown_files = []
    for current_directory, _, files in os.walk(vault_root_directory):
        for file_name in files:
            if file_name.endswith(MARKDOWN_EXTENSION):
                full_file_path = os.path.join(current_directory, file_name)
                markdown_files.append(full_file_path)
    return markdown_files


def get_words_to_filter():
    filter_choice = (
        input("Do you want to filter any words? (yes/no): ").strip().lower()
    )
    if filter_choice == "yes":
        words_input = input(
            "Enter words to filter, separated by commas (e.g., word1, word2): "
        )
        return [word.strip() for word in words_input.split(",") if word.strip()]
    return []


def apply_word_filter(content, words_to_filter):
    if not words_to_filter:
        return content

    for word in words_to_filter:
        pattern = r"\b" + re.escape(word) + r"\b"
        content = re.sub(pattern, "REDACTED", content, flags=re.IGNORECASE)
    return content


def generate_directory_tree(vault_path, md_files):
    tree_lines = ["Directory structure:\n"]
    file_tree = {}

    for md_file in md_files:
        relative_path = os.path.relpath(md_file, vault_path)
        parts = relative_path.split(os.sep)
        current_level = file_tree
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

    def build_tree_str(directory, prefix=""):
        folders = sorted(
            [name for name, content in directory.items() if content])

        for i, name in enumerate(folders):
            is_last = i == len(folders) - 1
            connector = "└── " if is_last else "├── "
            tree_lines.append(f"{prefix}{connector}{name}/\n")
            new_prefix = "    " if is_last else "│   "
            build_tree_str(directory[name], prefix + new_prefix)

    root_name = os.path.basename(vault_path)
    tree_lines.append(f"└── {root_name}/\n")
    build_tree_str(file_tree, "    ")

    return "".join(tree_lines)


def combine_files(file_paths, base_directory, words_to_filter):
    combined_content = []

    for file_path in file_paths:
        try:
            relative_path = os.path.relpath(file_path, base_directory)
            header = f"{FILE_HEADER_PREFIX}{relative_path}\n"

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = apply_word_filter(content, words_to_filter)

            combined_content.append(header)
            combined_content.append(content)
            combined_content.append(FILE_SEPARATOR)

        except UnicodeDecodeError:
            print(
                f"WARNING: Could not read file '{file_path}' due to encoding error. Skipping."
            )
        except Exception as e:
            print(
                f"WARNING: An error occurred while reading file '{file_path}': {e}. Skipping."
            )
    return "".join(combined_content)


def write_to_output_file(content_to_write, output_file_path):
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(content_to_write)
            print(f"\nIngested notes saved to {output_file_path}")
    except Exception as e:
        print(f"ERROR: Could not write because: {e}")


def main():
    vault_path = get_vault_path()
    output_path = get_output_path()
    words_to_filter = get_words_to_filter()

    resolved_vault_path = os.path.abspath(os.path.expanduser(vault_path))
    resolved_output_path = os.path.abspath(os.path.expanduser(output_path))

    final_combined_notes_file = os.path.join(
        resolved_output_path, DEFAULT_OUTPUT_FILENAME
    )

    print(f"\nVault Path: {resolved_vault_path}")
    print(f"Output Directory: {resolved_output_path}")
    print(f"Combined notes will be saved to: {final_combined_notes_file}")
    if words_to_filter:
        print(f"Words to filter: {', '.join(words_to_filter)}")

    found_markdown_files = get_file_names(resolved_vault_path)

    directory_tree = generate_directory_tree(
        resolved_vault_path, found_markdown_files
    )

    combined_content = combine_files(
        found_markdown_files, resolved_vault_path, words_to_filter
    )

    final_output = directory_tree + FILE_SEPARATOR + combined_content

    write_to_output_file(final_output, final_combined_notes_file)

    print("\n--- Ingest Complete ---\n")


if __name__ == "__main__":
    main()
