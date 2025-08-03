import os


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


def main():

    print("Obsidian Markdown Ingester: ")

    vault_path = get_vault_path()
    output_path = get_output_path()
    print(f"Output path: {output_path}, Vault path: {vault_path}")


if __name__ == "__main__":
    main()
