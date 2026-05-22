import argparse
import sys
from pathlib import Path
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description="Count lines, words, and characters in a text file.")
    parser.add_argument("path_to_text_file", type=Path, help="Path to the UTF-8 text file")
    return parser.parse_args()

def count_text_file(file_path):
    try:
        with file_path.open('r', encoding='utf-8') as file:
            content = file.read()
            lines = content.splitlines()
            words = content.split()
            char_count = sum(len(word) for word in words)
            nonempty_line_count = sum(1 for line in lines if line.strip())
            return {
                "line_count": len(lines),
                "word_count": len(words),
                "char_count": char_count,
                "nonempty_line_count": nonempty_line_count
            }
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    args = parse_arguments()
    if not args.path_to_text_file.exists() or not args.path_to_text_file.is_file():
        print("Error: File does not exist or is not a file.", file=sys.stderr)
        sys.exit(1)

    output = count_text_file(args.path_to_text_file)
    print(json.dumps(output))

if __name__ == "__main__":
    main()
