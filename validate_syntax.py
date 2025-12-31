#!/usr/bin/env python3
"""
Quick validation script to check if the code structure is correct
"""

import sys
import ast


def check_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, "r") as f:
            code = f.read()
        ast.parse(code)
        print(f"✓ {file_path}: Valid syntax")
        return True
    except SyntaxError as e:
        print(f"✗ {file_path}: Syntax error at line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"✗ {file_path}: Error: {str(e)}")
        return False


if __name__ == "__main__":
    files_to_check = [
        "models.py",
        "config.py",
        "scraper.py",
        "app.py",
        "utils.py",
        "s3_upload.py",
    ]

    print("Checking Python syntax...\n")
    all_valid = True
    for file in files_to_check:
        if not check_syntax(file):
            all_valid = False

    print("\n" + "=" * 50)
    if all_valid:
        print("✓ All files have valid Python syntax!")
    else:
        print("✗ Some files have syntax errors")
        sys.exit(1)
