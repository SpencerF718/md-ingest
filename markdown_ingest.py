import os
import re
import json

MARKDOWN_EXTENSION = ".md"
DEFAULT_OUTPUT_FILENAME = "md_ingest.txt"

DEFAULT_TOKEN_LIMIT = 50000
CHARACTERS_PER_TOKEN = 4

FILE_SEPARATOR = "\n\n" + "=" * 80 + "\n\n"
FILE_HEADER_PREFIX = "FILE: "

CONFIG_FILE_NAME = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE_NAME):
        with open(CONFIG_FILE_NAME, 'r') as f:
            return json.load(f)
    return {}


def get_vault_path(config):
    vault_path_default = config.get("vault_path", "")
    vault_found = False
    vault_path = ""

    while not vault_found:
        prompt = "Please enter the absolute path to your Obsidian vault"
        if vault_path_default:
            prompt += f" (default: {vault_path_default})"
        prompt += ": "
        vault_path = input(prompt) or vault_path_default

        if os.path.isabs(vault_path) and os.path.isdir(vault_path):
            vault_found = True
        else:
            print(
                "ERROR: Invalid or non-existent directory. Please enter a valid absolute path."
            )

    return vault_path


def get_output_path(config):
    output_path_default = config.get("output_path", "")
    output_found = False
    output_path = ""

    while not output_found:
        prompt = "Please enter the absolute path to your output directory"
        if output_path_default:
            prompt += f" (default: {output_path_default})"
        prompt += ": "
        output_path = input(prompt) or output_path_default

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


def get_words_to_filter(config):
    words_to_filter_default = config.get("words_to_filter", [])

    prompt = "Do you want to filter any words? (yes/no)"
    if words_to_filter_default:
        default_str = ", ".join(words_to_filter_default)
        prompt += f" (current defaults: {default_str})"
    prompt += ": "

    filter_choice = input(prompt).strip().lower()

    if filter_choice in ["yes", "y"]:
        words_input = input(
            "Enter words to filter, separated by commas (e.g., word1, word2): "
        )
        return [word.strip() for word in words_input.split(",") if word.strip()]
    elif words_to_filter_default and filter_choice in ["no", "n"]:
        return []
    elif words_to_filter_default:
        print("Using words from config file.")
        return words_to_filter_default
    return []


def get_splitting_preference(config):
    default_token_limit = config.get("token_limit", DEFAULT_TOKEN_LIMIT)
    split_choice = input(
        "Do you want to split the output into multiple files? (yes/no): ").strip().lower()

    if split_choice in ["yes", "y"]:
        while True:
            try:
                prompt = "Enter the token limit per file"
                if default_token_limit:
                    prompt += f" (default: {default_token_limit})"
                prompt += ": "
                limit_input = input(prompt)

                token_limit = int(
                    limit_input) if limit_input else default_token_limit

                if token_limit > 0:
                    return token_limit * CHARACTERS_PER_TOKEN
                else:
                    print("Please enter a positive number for the token limit.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    return 0


def get_file_names(vault_root_directory):
    markdown_files = []
    for current_directory, _, files in os.walk(vault_root_directory):
        for file_name in files:
            if file_name.endswith(MARKDOWN_EXTENSION):
                full_file_path = os.path.join(current_directory, file_name)
                markdown_files.append(full_file_path)
    return markdown_files


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


def write_to_output_file(content_to_write, output_file_path, split_character_limit):
    if split_character_limit <= 0 or len(content_to_write) <= split_character_limit:
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(content_to_write)
            print(f"\nIngested notes saved to {output_file_path}")
        except Exception as e:
            print(f"ERROR: Could not write because: {e}")
    else:
        base_name, ext = os.path.splitext(output_file_path)
        part_number = 1
        current_position = 0

        while current_position < len(content_to_write):
            end_position = min(current_position +
                               split_character_limit, len(content_to_write))
            potential_chunk = content_to_write[current_position:end_position]
            last_separator_index = potential_chunk.rfind(FILE_SEPARATOR)

            if last_separator_index != -1 and (len(potential_chunk) - last_separator_index) < (split_character_limit / 2):
                split_at = current_position + \
                    last_separator_index + len(FILE_SEPARATOR)
            else:
                split_at = end_position

            if (split_at < len(content_to_write) and content_to_write[split_at - len(FILE_SEPARATOR): split_at] == FILE_SEPARATOR):
                pass
            elif split_at < len(content_to_write):
                next_separator_index = content_to_write.find(
                    FILE_SEPARATOR, split_at - len(FILE_SEPARATOR))
                if (next_separator_index != -1 and (next_separator_index - current_position) < (split_character_limit + len(FILE_SEPARATOR) * 2)):
                    split_at = next_separator_index + len(FILE_SEPARATOR)

            current_part_content = content_to_write[current_position:split_at]
            output_file_name = f"{base_name}_part{part_number}{ext}"

            try:
                with open(output_file_name, "w", encoding="utf-8") as f:
                    f.write(current_part_content)
                print(
                    f"Ingested notes part {part_number} saved to {output_file_name}"
                )
            except Exception as e:
                print(
                    f"ERROR: Could not write part {part_number} because: {e}")

            current_position = split_at
            part_number += 1


def process_and_write_files(vault_path, output_path, words_to_filter, split_character_limit):
    resolved_vault_path = os.path.abspath(os.path.expanduser(vault_path))
    resolved_output_path = os.path.abspath(os.path.expanduser(output_path))
    final_combined_notes_file = os.path.join(
        resolved_output_path, DEFAULT_OUTPUT_FILENAME
    )

    print(f"\nVault Path: {resolved_vault_path}")
    print(f"Output Directory: {resolved_output_path}")
    print(f"Combined notes will be saved to: {final_combined_notes_file}\n")
    if words_to_filter:
        print(f"Words to filter: {', '.join(words_to_filter)}")
    if split_character_limit > 0:
        display_token_limit = split_character_limit // CHARACTERS_PER_TOKEN
        print(
            f"Output will be split into files of approximately {display_token_limit} tokens each.")

    found_markdown_files = get_file_names(resolved_vault_path)
    directory_tree = generate_directory_tree(
        resolved_vault_path, found_markdown_files
    )
    combined_content = combine_files(
        found_markdown_files, resolved_vault_path, words_to_filter
    )
    final_output = directory_tree + FILE_SEPARATOR + combined_content

    write_to_output_file(
        final_output, final_combined_notes_file, split_character_limit)
    print("\n--- Ingest Complete ---\n")


def main():
    config = load_config()

    if config.get("vault_path") and config.get("output_path"):
        use_defaults = input(
            "Config file found with vault and output paths. Use defaults? (y/n): ").strip().lower()
        if use_defaults in ["yes", "y"]:
            vault_path = config.get("vault_path")
            output_path = config.get("output_path")
            words_to_filter = config.get("words_to_filter", [])
            split_character_limit = config.get(
                "token_limit", 0) * CHARACTERS_PER_TOKEN

            process_and_write_files(
                vault_path, output_path, words_to_filter, split_character_limit)
            return

    vault_path = get_vault_path(config)
    output_path = get_output_path(config)
    words_to_filter = get_words_to_filter(config)
    split_character_limit = get_splitting_preference(config)

    process_and_write_files(vault_path, output_path,
                            words_to_filter, split_character_limit)


if __name__ == "__main__":
    main()
