# md-ingest
A Python tool to consolidate Markdown notes from an Obsidian vault into a single, structured text file for LLM ingestion.

## Features 

- **Vault Search:** Scans over a user-specificed Obsidian vault for all .md files.
- **Directory Tree:** Displays a directory tree in the output .txt file for better context and referencing.
- **File Separators:** Clearly separates each note with a separator bar followed by the file path and name.
- **Word Filtering:** Allows the user to specify a list of sensitive or otherwise unwanted words to be redacted from the output.
- **Output Splitting:** Allows the user to split the output into multiple files based on a configurable token limit.
- **Config File:** Includes a 'config.json' file for storing default settings.

## How to Use

1. Run the script:
```bash
python markdown_ingest.py
```
2. Follow the prompts

## Configuration Options

If you need to frequently use this tool, the `config.json` file will be useful.  Here is a key for the config:

| Key               | Description                                                                                             | Example Value                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `vault_path`      | The absolute path to your Obsidian vault. The script will search this directory and all its subdirectories. | `"C:\\Users\\Name\\Documents\\Obsidian"` |
| `output_path`     | The absolute path to the directory where the output text file(s) will be saved.                         | `"C:\\Users\\Name\\Documents\\Output"`        |
| `token_limit`     | An integer representing the maximum number of tokens per output file. `0` disables splitting.           | `50000`                                             |
| `words_to_filter` | A list of strings. Any word in this list will be replaced with "REDACTED" in the output.                | `["password", "private", "name"]`                           |

## Credit

Inspired by the [gitingest repo](https://github.com/coderamp-labs/gitingest)
