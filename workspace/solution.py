import argparse
import json
import sys

def count_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    line_count = len(content.splitlines())
    word_count = sum(len(line.split()) for line in content.splitlines())
    char_count = len(content)
    
    return {
        "line_count": line_count,
        "word_count": word_count,
        "char_count": char_count
    }

def main():
    parser = argparse.ArgumentParser(description="Count lines, words, and characters in a text file.")
    parser.add_argument("path", type=str, help="Path to the UTF-8 encoded text file")
    
    args = parser.parse_args()
    
    try:
        result = count_file(args.path)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
