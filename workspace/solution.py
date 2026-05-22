import argparse
import json
import sys

def count_text_elements(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.splitlines()
            line_count = len(lines)
            word_count = sum(len(line.split()) for line in lines)
            char_count = len(content)
            return {
                "line_count": line_count,
                "word_count": word_count,
                "char_count": char_count
            }
    except FileNotFoundError:
        print("Error: File not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Text Counter")
    parser.add_argument('file_path', type=str, help='Path to the UTF-8 text file')
    
    args = parser.parse_args()
    
    if len(sys.argv) != 2:
        print("Error: Incorrect number of arguments.", file=sys.stderr)
        sys.exit(1)
    
    result = count_text_elements(args.file_path)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
