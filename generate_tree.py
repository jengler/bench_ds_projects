#!/usr/bin/env python3
"""
Generate a directory tree structure with configurable depth, breadth,
file count, file size, and notebook percentage.
"""

import argparse
import os
import random
import string
import sys


NOTEBOOK_HEADER = "# Databricks notebook source\n"


def random_text(size_bytes: int) -> str:
    """Return a string of approximately *size_bytes* bytes of random printable data."""
    chars = string.ascii_letters + string.digits + " \n"
    return "".join(random.choices(chars, k=size_bytes))


def create_file(path: str, size_bytes: int, is_notebook: bool) -> None:
    """Write a single .txt or .py notebook file of the requested size."""
    with open(path, "w") as f:
        if is_notebook:
            f.write(NOTEBOOK_HEADER)
            remaining = max(0, size_bytes - len(NOTEBOOK_HEADER))
            f.write(random_text(remaining))
        else:
            f.write(random_text(size_bytes))


def build_tree(
    root: str,
    depth: int,
    breadth: int,
    files_per_folder: int,
    file_size: int,
    pct_notebooks: float,
) -> None:
    """Recursively build the directory tree and populate it with files."""
    os.makedirs(root, exist_ok=True)

    # Determine how many notebooks vs plain text files in this folder
    num_notebooks = round(files_per_folder * pct_notebooks / 100.0)
    num_txt = files_per_folder - num_notebooks

    # Build a shuffled list so notebooks and txt files are interleaved randomly
    file_types = (["notebook"] * num_notebooks) + (["txt"] * num_txt)
    random.shuffle(file_types)

    for idx, ftype in enumerate(file_types):
        if ftype == "notebook":
            name = f"file_{idx}.py"
            create_file(os.path.join(root, name), file_size, is_notebook=True)
        else:
            name = f"file_{idx}.txt"
            create_file(os.path.join(root, name), file_size, is_notebook=False)

    # Recurse into child directories if we haven't hit the depth limit
    if depth > 1:
        for b in range(breadth):
            child_dir = os.path.join(root, f"dir_{b}")
            build_tree(child_dir, depth - 1, breadth, files_per_folder, file_size, pct_notebooks)


def parse_size(value: str) -> int:
    """Parse a human-friendly size string (e.g. '4KB', '1MB') into bytes."""
    value = value.strip().upper()
    multipliers = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
    for suffix, mult in sorted(multipliers.items(), key=lambda x: -len(x[0])):
        if value.endswith(suffix):
            number = value[: -len(suffix)].strip()
            return int(float(number) * mult)
    # No suffix — treat as raw byte count
    return int(value)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a directory tree with configurable depth, breadth, files, size, and notebook ratio."
    )
    parser.add_argument(
        "--depth",
        type=int,
        required=True,
        help="How many folders deep the tree goes.",
    )
    parser.add_argument(
        "--breadth",
        type=int,
        required=True,
        help="How many child folders each directory contains.",
    )
    parser.add_argument(
        "--files-per-folder",
        type=int,
        required=True,
        help="Number of files to create in each folder.",
    )
    parser.add_argument(
        "--file-size",
        type=str,
        required=True,
        help="Size of each file (e.g. 1024, 4KB, 1MB).",
    )
    parser.add_argument(
        "--pct-notebooks",
        type=float,
        required=True,
        help="Percentage (0-100) of files that are Databricks notebooks (.py).",
    )
    parser.add_argument(
        "--root",
        type=str,
        default="generated_tree",
        help="Root directory for the generated tree (default: generated_tree).",
    )

    args = parser.parse_args()

    if args.depth < 1:
        parser.error("--depth must be >= 1")
    if args.breadth < 1:
        parser.error("--breadth must be >= 1")
    if args.files_per_folder < 0:
        parser.error("--files-per-folder must be >= 0")
    if not (0 <= args.pct_notebooks <= 100):
        parser.error("--pct-notebooks must be between 0 and 100")

    file_size = parse_size(args.file_size)

    # Summary before starting
    # Total folders = (breadth^depth - 1) / (breadth - 1) when breadth > 1, else depth
    if args.breadth == 1:
        total_folders = args.depth
    else:
        total_folders = (args.breadth ** args.depth - 1) // (args.breadth - 1)
    total_files = total_folders * args.files_per_folder
    total_bytes = total_files * file_size

    print(f"Root directory : {args.root}")
    print(f"Depth          : {args.depth}")
    print(f"Breadth        : {args.breadth}")
    print(f"Files/folder   : {args.files_per_folder}")
    print(f"File size      : {file_size} bytes")
    print(f"Notebooks      : {args.pct_notebooks}%")
    print(f"Total folders  : {total_folders}")
    print(f"Total files    : {total_files}")
    print(f"Est. total size: {total_bytes / 1024 / 1024:.2f} MB")
    print()

    build_tree(
        root=args.root,
        depth=args.depth,
        breadth=args.breadth,
        files_per_folder=args.files_per_folder,
        file_size=file_size,
        pct_notebooks=args.pct_notebooks,
    )

    print("Done.")


if __name__ == "__main__":
    main()

