import sys
import json

def count_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.splitlines()
            line_count = len(lines)
            word_count = sum(len(line.split()) for line in lines)
            char_count = len(content)
            result = {
                "line_count": line_count,
                "word_count": word_count,
                "char_count": char_count
            }
            print(json.dumps(result))
    except FileNotFoundError:
        sys.stderr.write(f"Error: File '{file_path}' not found.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python solution.py <file_path>\n")
        sys.exit(1)
    
    file_path = sys.argv[1]
    count_text(file_path)
