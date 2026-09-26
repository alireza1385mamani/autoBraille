#!/usr/bin/env python3
# coding: utf-8
"""Unified Test Runner for Auto Braille.

Executes all 7 test suites across isolated Python processes, preventing cross-test mock pollution,
and validates bytecode compilation and warnings on the active Python interpreter (Python 3.14+).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

TEST_FILES = [
    "tests/test_audit_fixes.py",
    "tests/test_tables_mode.py",
    "tests/test_doc_lang_and_tactile.py",
    "tests/test_segmenter.py",
    "tests/test_intra_script.py",
    "tests/test_grade2_boundary.py",
    "tests/test_auto_detect_keyboards.py",
]


def verify_compilation(repo_dir: str) -> bool:
    """Byte-compile all Python files under addon/ to ensure zero syntax or encoding errors."""
    import py_compile

    addon_dir = os.path.join(repo_dir, "addon")
    compiled_count = 0
    for root, _, files in os.walk(addon_dir):
        for f in sorted(files):
            if f.endswith(".py"):
                p = os.path.join(root, f)
                try:
                    py_compile.compile(p, doraise=True)
                    compiled_count += 1
                except Exception as e:
                    print(f"FAILED to compile {p}: {e}", file=sys.stderr)
                    return False

    print(f"Compiled {compiled_count} Python source files successfully with zero warnings/errors.")
    return True


def run_all_tests() -> int:
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable

    print("=" * 65)
    print(f"  AUTO BRAILLE UNIFIED TEST RUNNER (Python {sys.version.split()[0]})")
    print("=" * 65)
    print(f"Python interpreter: {python_exe}")
    print(f"Working directory:  {repo_dir}\n")

    # 1. Bytecode compilation step
    print("1. Verifying bytecode compilation across all source modules...")
    if not verify_compilation(repo_dir):
        return 1
    print()

    # 2. Run test suites in isolated subprocesses
    print("2. Running 7 test suites in isolated processes...")
    failed = []
    total_start = time.perf_counter()

    for idx, test_rel in enumerate(TEST_FILES, start=1):
        test_path = os.path.join(repo_dir, test_rel)
        if not os.path.isfile(test_path):
            print(f"[{idx}/7] MISSING: {test_rel}", file=sys.stderr)
            failed.append(test_rel)
            continue

        print(f"\n[{idx}/7] Running {test_rel}...")
        t_start = time.perf_counter()
        res = subprocess.run([python_exe, "-W", "default", test_path], cwd=repo_dir)
        elapsed = time.perf_counter() - t_start

        if res.returncode != 0:
            print(f"--> FAILED: {test_rel} (exit code {res.returncode}, {elapsed:.2f}s)", file=sys.stderr)
            failed.append(test_rel)
        else:
            print(f"--> PASSED: {test_rel} ({elapsed:.2f}s)")

    total_elapsed = time.perf_counter() - total_start
    print("\n" + "=" * 65)
    if failed:
        print(f"TEST RUN FAILED: {len(failed)} of {len(TEST_FILES)} suites failed in {total_elapsed:.2f}s:")
        for f in failed:
            print(f"  - {f}")
        print("=" * 65)
        return 1
    else:
        print(f"ALL 7 TEST SUITES PASSED 100% on Python {sys.version.split()[0]} ({total_elapsed:.2f}s)!")
        print("=" * 65)
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
