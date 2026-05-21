import json
import sys

def main():
    try:
        input_data = sys.stdin.read()
        lines = input_data.splitlines()
        
        # Count lines containing "No Rows"
        no_rows_count = sum(1 for line in lines if "No Rows" in line.strip())
        
        # Calculate other counts
        total_lines = len(lines)
        word_count = sum(len(line.split()) for line in lines)
        char_count = sum(len(line) for line in lines)
        
        result = {
            "nonempty_line_count": no_rows_count,
            "line_count": total_lines,
            "word_count": word_count,
            "char_count": char_count,
        }
        
        print(json.dumps(result))
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
