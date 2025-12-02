#!/usr/bin/env python3
"""
Script to convert PyQt5 imports to PyQt6
แปลง imports จาก PyQt5 เป็น PyQt6 อัตโนมัติ
"""
import os
import re
from pathlib import Path

def convert_file(file_path):
    """Convert PyQt5 imports to PyQt6 in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Replace imports
    replacements = [
        (r'from PyQt5\.QtWidgets import', 'from PyQt6.QtWidgets import'),
        (r'from PyQt5\.QtCore import', 'from PyQt6.QtCore import'),
        (r'from PyQt5\.QtGui import', 'from PyQt6.QtGui import'),
        (r'from PyQt6 import QtWidgets', 'from PyQt6 import QtWidgets'),
        (r'from PyQt6 import QtCore', 'from PyQt6 import QtCore'),
        (r'from PyQt6 import QtGui', 'from PyQt6 import QtGui'),
        (r'import PyQt6', 'import PyQt6'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Known API changes (optional - most code will work without these)
    api_changes = [
        # Exec method
        (r'\.exec_\(\)', '.exec()'),

        # Alignment flags (if used with full path)
        (r'Qt\.AlignCenter', 'Qt.AlignmentFlag.AlignCenter'),
        (r'Qt\.AlignLeft', 'Qt.AlignmentFlag.AlignLeft'),
        (r'Qt\.AlignRight', 'Qt.AlignmentFlag.AlignRight'),
        (r'Qt\.AlignTop', 'Qt.AlignmentFlag.AlignTop'),
        (r'Qt\.AlignBottom', 'Qt.AlignmentFlag.AlignBottom'),
    ]

    for pattern, replacement in api_changes:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Convert all Python files in the project"""
    print("=" * 70)
    print("  PyQt5 → PyQt6 Converter")
    print("=" * 70)
    print()

    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip venv and __pycache__
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'build', 'dist']]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    print(f"Found {len(python_files)} Python files")
    print()

    converted_count = 0
    for file_path in python_files:
        if convert_file(file_path):
            print(f"✓ Converted: {file_path}")
            converted_count += 1

    print()
    print("=" * 70)
    print(f"  Conversion Complete!")
    print(f"  Files converted: {converted_count}/{len(python_files)}")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Install PyQt6: pip install PyQt6")
    print("  2. Test the application: python main.py")
    print()

if __name__ == "__main__":
    main()
