#!/usr/bin/env python3
# coding: utf-8
"""Packaging script for Auto Braille NVDA Add-on.

Bundles the contents of the `addon/` directory into a clean, distributable
`<name>-<version>.nvda-addon` package without any `__pycache__` or development files.
"""

from __future__ import annotations

import configparser
import os
import sys
import zipfile

def read_manifest_info(addon_dir: str) -> tuple[str, str]:
    manifest_path = os.path.join(addon_dir, "manifest.ini")
    if not os.path.isfile(manifest_path):
        raise FileNotFoundError(f"manifest.ini not found at {manifest_path}")

    # Read using utf-8-sig to handle possible BOM
    with open(manifest_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    # Prepend dummy section header if missing for configparser
    content = "[DEFAULT]\n" + "".join(lines)
    cp = configparser.ConfigParser()
    cp.read_string(content)

    name = cp.get("DEFAULT", "name", fallback="autoBraille").strip().strip('"').strip("'")
    version = cp.get("DEFAULT", "version", fallback="1.0.0").strip().strip('"').strip("'")
    return name, version

def build_addon(repo_dir: str) -> str:
    addon_dir = os.path.join(repo_dir, "addon")
    if not os.path.isdir(addon_dir):
        raise FileNotFoundError(f"addon directory not found at {addon_dir}")

    name, version = read_manifest_info(addon_dir)
    output_filename = f"{name}-{version}.nvda-addon"
    output_path = os.path.join(repo_dir, output_filename)

    if os.path.exists(output_path):
        os.remove(output_path)

    print(f"Building {output_filename} from {addon_dir}...")

    file_count = 0
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(addon_dir):
            # Prune __pycache__ and hidden directories in-place
            dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]

            for file in sorted(files):
                if file.endswith((".pyc", ".pyo")) or file.startswith("."):
                    continue

                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, addon_dir)
                z.write(abs_path, arcname=rel_path)
                file_count += 1
                size = os.path.getsize(abs_path)
                print(f"  + {rel_path} ({size:,} bytes)")

    total_size = os.path.getsize(output_path)
    print(f"\nSuccessfully built {output_filename} ({total_size:,} bytes, {file_count} files).")
    print(f"Location: {output_path}")
    return output_path

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        build_addon(current_dir)
    except Exception as e:
        print(f"Error building add-on: {e}", file=sys.stderr)
        sys.exit(1)
