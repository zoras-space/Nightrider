import argparse
import sys
import json

def count_text_metrics(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except (IOError, PermissionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    lines = content.splitlines()
    line_count = len(lines)
    word_count = sum(len(line.split()) for line in lines)
    char_count = len(content)
    
    nonempty_line_count = sum(1 for line in lines if line.strip())
    
    result = {
        "line_count": line_count,
        "word_count": word_count,
        "char_count": char_count,
        "nonempty_line_count": nonempty_line_count
    }

    return result

def main():
    parser = argparse.ArgumentParser(description="Text Counter")
    parser.add_argument("file_path", type=str, help="Path to the UTF-8 text file")

    args = parser.parse_args()

    if len(args.file_path) == 0:
        print("Error: No file path provided.", file=sys.stderr)
        sys.exit(1)

    try:
        metrics = count_text_metrics(args.file_path)
        json_output = f'{{"line_count": {metrics["line_count"]}, "word_count": {metrics["word_count"]}, "char_count": {metrics["char_count"]}, "nonempty_line_count": {metrics["nonempty_line_count"]}}}'
        print(json_output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
