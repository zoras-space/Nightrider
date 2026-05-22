import sys
import json

def count_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.splitlines()
            line_count = len(lines)
            word_count = sum(len(line.split()) for line in lines)
            char_count = len(content)
            nonempty_line_count = sum(1 for line in lines if line.strip())
            return {
                "line_count": line_count,
                "word_count": word_count,
                "char_count": char_count,
                "nonempty_line_count": nonempty_line_count
            }
    except FileNotFoundError:
        print("Error: Unable to read file", file=sys.stderr)
        sys.exit(2)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 text_counter.py <path_to_text_file>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    result = count_text_file(file_path)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
