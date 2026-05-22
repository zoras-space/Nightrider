import sys
import json

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Error: Expected exactly one positional argument (path to text file).\n")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            line_count = len(content.splitlines())
            word_count = len(content.split())
            char_count = len(content)
    except FileNotFoundError:
        sys.stderr.write(f"Error: Unable to read file at {file_path}.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    result = {
        "line_count": line_count,
        "word_count": word_count,
        "char_count": char_count,
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
