#!/usr/bin/env python3
"""
patch.py — shows a unified diff for a targeted string replacement
Usage: python patch.py <file_path> <old_string> <new_string>
Prints diff only. Does NOT write — agent writes after confirmation.
"""
import sys
import difflib

def main():
    if len(sys.argv) < 4:
        print("Usage: patch.py <file_path> <old_string> <new_string>")
        sys.exit(1)

    file_path = sys.argv[1]
    old_str = sys.argv[2]
    new_str = sys.argv[3]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)

    if old_str not in original:
        print(f"ERROR: Target string not found in {file_path}")
        sys.exit(1)

    patched = original.replace(old_str, new_str, 1)

    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        patched.splitlines(keepends=True),
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
    )

    diff_output = "".join(diff)
    print(diff_output if diff_output else "No changes detected.")

if __name__ == "__main__":
    main()