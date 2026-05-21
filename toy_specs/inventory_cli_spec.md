# Toy Spec: Inventory CLI

Write a Python CLI program that accepts exactly one positional argument: the path to a UTF-8 command file.

Each non-empty line in the file is one command:

- `ADD item qty`: increase an item's quantity by `qty`.
- `REMOVE item qty`: decrease an item's quantity by `qty`.
- `TOTAL`: record the current total quantity across all items.

Items are case-sensitive strings without spaces. Quantities are nonnegative integers.

At the end, print one JSON object to stdout:

```json
{
  "inventory": {"item": qty},
  "totals": [number]
}
```

Only include inventory items with quantities greater than zero. Sort inventory keys alphabetically in the output JSON.

Behavior:

- On success, print only JSON to stdout and exit with code `0`.
- If the argument count is wrong, print a helpful error to stderr and exit nonzero.
- If the file cannot be read, print a helpful error to stderr and exit nonzero.
- If a command is malformed, print a helpful error to stderr and exit nonzero.
- Removing more than available should be an error.
- Use only the Python standard library.

