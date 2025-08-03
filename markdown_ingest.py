import os


def get_vault_path():

    vault_found = False
    vault_path = ""

    while not vault_found:
        vault_path = input(
            r"Please enter the absolute path to your Obsidian vault. e.g. C:\Users\Name\OneDrive\Documents\Main")

        if os.path.isabs(vault_path):
            vault_found = True
        else:
            print("ERROR: Invalid path.")

    return vault_path


def main():

    print("Obsidian Markdown Ingester: ")

    vault_path = get_vault_path()
