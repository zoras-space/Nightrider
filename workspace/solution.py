import argparse
import json
import sys

def count_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            line_count = 0
            word_count = 0
            char_count = 0
            
            for line in file:
                line_count += 1
                words = line.split()
                word_count += len(words)
                char_count += len(line)
            
            return {
                "line_count": line_count,
                "word_count": word_count,
                "char_count": char_count,
            }
    except FileNotFoundError:
        print("Error: Unable to read file.", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Count characters, words, and lines in a text file.")
    parser.add_argument('file_path', type=str, help='Path to the UTF-8 text file')
    
    args = parser.parse_args()
    
    
    result = count_text(args.file_path)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
