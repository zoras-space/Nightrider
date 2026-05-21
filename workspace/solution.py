import sys
import json

def main():
    if len(sys.argv) != 2:
        print("Usage: python solution.py <path_to_text_file>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError:
        print(f"Error: Unable to read file '{file_path}'.", file=sys.stderr)
        sys.exit(1)

    line_count = len(content.splitlines())
    word_count = len(content.split())
    char_count = len(content)

    output = {
        "line_count": line_count,
        "word_count": word_count,
        "char_count": char_count
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()
