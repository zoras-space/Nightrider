import json
import os
import sys

INPUT_FILE = 'input.txt'
OUTPUT_FILE = 'output.json'

def read_input_file(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        raise ValueError("Input file must be a non-empty file.")
    with open(file_path, 'r') as file:
        return file.read().strip()

def parse_data(data):
    lines = data.split('\n')
    if len(lines) != 2:
        raise ValueError("Input file must contain exactly two rows.")
    k1, p1 = lines
    return {
        "k1": str(k1).strip(),
        "p1": str(p1).strip()
    }

def write_output_file(data, output_path):
    if os.path.exists(output_path):
        raise ValueError("Output file already exists. Please specify a different output file name.")
    with open(output_path, 'w') as file:
        json.dump(data, file)

def main():
    try:
        input_data = read_input_file(INPUT_FILE)
        parsed_data = parse_data(input_data)
        write_output_file(parsed_data, OUTPUT_FILE)
        print(json.dumps(parsed_data))
    except ValueError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
