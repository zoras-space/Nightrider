# Toy Spec: JSON Transformer

Write a Python CLI program that accepts exactly one positional argument: the path to a UTF-8 JSON file.

The input file contains a JSON array of objects. For each object, output a normalized object with:

- `id`: copied from the input `id`.
- `name`: copied from the input `name`, stripped of surrounding whitespace.
- `active`: boolean copied from input `active`; if missing, default to `false`.

The output must be a JSON array printed to stdout. Preserve input order.

Behavior:

- On success, print only JSON to stdout and exit with code `0`.
- If the argument count is wrong, print a helpful error to stderr and exit nonzero.
- If the file is not valid JSON, print a helpful error to stderr and exit nonzero.
- If the root JSON value is not an array, print a helpful error to stderr and exit nonzero.
- If any item is not an object or is missing `id` or `name`, print a helpful error to stderr and exit nonzero.
- Use only the Python standard library.

