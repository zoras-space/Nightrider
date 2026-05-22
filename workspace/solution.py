import sys
import json

def count_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.splitlines()
            words = content.split()
            char_count = len(content)
            line_count = len(lines)
            word_count = len(words)
            return {
                "line_count": line_count,
                "word_count": word_count,
                "char_count": char_count
            }
    except FileNotFoundError:
        sys.stderr.write(f"Error: File '{file_path}' not found.\n")
        sys.exit(2)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(2)

if len(sys.argv) != 2:
    sys.stderr.write("Usage: python3 text_counter.py <path_to_text_file>\n")
    sys.exit(1)

file_path = sys.argv[1]
result = count_text(file_path)
print(json.dumps(result))
sys.exit(0)
