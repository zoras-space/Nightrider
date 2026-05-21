# Toy Spec: Text Counter Repair Drill

Write a Python CLI program that accepts exactly one positional argument: the path to a UTF-8 text file.

The program must read the file and print one JSON object to stdout with these integer fields:

- `line_count`: number of lines in the file, using Python's `splitlines()` behavior.
- `word_count`: number of whitespace-separated words.
- `char_count`: number of characters in the file.
- `nonempty_line_count`: number of lines whose stripped content is not empty.

Behavior:

- On success, print only JSON to stdout and exit with code `0`.
- If the argument count is wrong, print a helpful error to stderr and exit nonzero.
- If the file cannot be read, print a helpful error to stderr and exit nonzero.
- Do not print debug text to stdout.
- Use only the Python standard library.

This spec is intentionally slightly different from `text_counter_spec.md` so the current text-counter solution should fail first and then be repaired by the agent.

