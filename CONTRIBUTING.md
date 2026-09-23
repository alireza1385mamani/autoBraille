# Contributing to Auto Braille

Thank you for your interest in improving **Auto Braille**! We welcome bug reports, feature suggestions, code contributions, and translations.

---

## Code of Conduct

Please maintain a respectful, welcoming, and inclusive environment for all contributors and users.

---

## How to Contribute

### 1. Reporting Bugs
* Search existing issues to ensure the bug hasn't already been reported.
* Open an issue providing:
  * NVDA version and Windows OS version.
  * Braille display model and connection method (USB/Bluetooth/Serial).
  * Auto Braille configuration (active tables, primary table, tactile indicators).
  * An NVDA debug log snippet (`NVDA Menu -> Tools -> View Log`).

### 2. Suggesting Features & New Languages
* Open an issue detailing the requested language/script, its writing system, and the recommended Liblouis table in NVDA.
* If applicable, provide the Unicode character ranges and standard Windows LANGIDs.

### 3. Submitting Pull Requests
1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Adhere to code conventions:
   * Python 3.10+ syntax with strict type annotations (`typing.NamedTuple`, `Optional`, `List`, `Dict`, `Tuple`, `Set`).
   * Indentation: tabs (standard for NVDA add-on codebase) or 4 spaces consistently.
   * Clear docstrings and comments explaining non-trivial logic.
   * Zero performance regressions on startup and scrolling.
3. Run the test suite:
   ```bash
   python tests/test_features_3_4.py
   python tests/test_tables_mode.py
   python tests/test_segmenter.py
   ```
4. Build the package to verify bundling:
   ```bash
   python build.py
   ```
5. Submit your pull request with a descriptive title and detailed summary of changes.
