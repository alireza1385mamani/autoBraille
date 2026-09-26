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

### 3. Adding Translations & Localization
* All user-facing strings must be wrapped in `_("...")` and immediately preceded by a `# Translators:` comment describing the UI context and control type.
* Run the catalog generator to refresh the template:
  ```bash
  py.exe generate_pot.py
  ```
* Translation files should be placed under `addon/locale/<lang>/LC_MESSAGES/autoBraille.po`.

### 4. Submitting Pull Requests
1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Adhere to code conventions:
   * Python 3.10+ syntax with strict type annotations (`typing.NamedTuple`, `Optional`, `List`, `Dict`, `Tuple`, `Set`).
   * Indentation: tabs (standard for the NVDA codebase).
   * Screen reader friendly: use descriptive identifiers (e.g. `cell_idx`, `char_idx`, `braille_cell`) rather than cryptic single letters.
   * NVDA Add-on Store compliance: guard settings panel registration against execution on Secure Desktop (`globalVars.appArgs.secureMode`).
   * Zero performance regressions on startup and rapid scrolling.
3. Run the complete test suite:
   ```bash
   py.exe tests/test_audit_fixes.py
   py.exe tests/test_tables_mode.py
   py.exe tests/test_doc_lang_and_tactile.py
   py.exe tests/test_segmenter.py
   py.exe tests/test_intra_script.py
   py.exe tests/test_grade2_boundary.py
   ```
   Or run all tests with the PowerShell build script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File build.ps1 -RunTests
   ```
4. Build the package to verify bundling:
   ```bash
   py.exe build.py
   ```
5. Submit your pull request with a descriptive title and detailed summary of changes.
