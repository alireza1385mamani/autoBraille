# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-09-25

### Fixed
- **NVDA Secure Desktop / UAC Compliance**: Guarded settings panel registration against execution on Windows Secure Desktops (`globalVars.appArgs.secureMode`), complying strictly with NVDA Add-on Store publishing guidelines to prevent unauthorized UI exposure during elevation prompts.
- **Translator Documentation Annotations**: Added explanatory `# Translators:` comments to all translatable UI elements, dialog controls, button labels, dropdown options, and gesture descriptions across `addon/globalPlugins/autoBraille/__init__.py` and `addon/globalPlugins/autoBraille/language_dialogs.py`.
- **Standardized Braille Pin Mask Constants**: Replaced magic hex literals (`0x40`, `0x80`, `0xC0`) in `translator.py` with descriptive, named constants (`BRAILLE_DOT_7`, `BRAILLE_DOT_8`, `BRAILLE_DOTS_7_8`) matching the ISO/TR 11548-1 8-dot braille standard.
- **Screen Reader & Braille Display Code Readability**: Refactored obscure single-character loop indices (`p`, `c`, `s`) in cursor routing and character mapping routines into semantic identifiers (`cell_idx`, `char_idx`, `braille_cell`), making the codebase significantly easier to audit and navigate with assistive tech.
- **Test Suite Module Mock Isolation**: Re-engineered mock module handling across all test suites to reuse existing modules in `sys.modules`, resolving cross-suite mock collisions when running under Python 3.14 via the Python Install Manager (`py.exe`).

### Added
- **Gettext Localization Catalog Tool (`generate_pot.py`)**: Added an automated template extraction script parsing manifest metadata and Python AST calls into `addon/locale/autoBraille.pot` for worldwide translators.
- **NVDA Add-on Store Metadata & Author Links**: Configured canonical repository URL and author contact links across `manifest.ini`, `readme.md`, and `readme.html`.

---

## [1.0.1] - 2026-09-25

### Fixed
- **64-bit Win32 Layout Detection Pointer Truncation**: Configured explicit `ctypes.wintypes` (`HWND`, `DWORD`, `HKL`) in `input_sync.py` to prevent 64-bit handle truncation and `ERROR_INVALID_WINDOW_HANDLE` failures.
- **Document Language Tag Mappings**: Aligned all `DOC_LANG_MAP` entries in `scripts_data.py` with valid script IDs across Odia (`indic_oriya`), Thai (`sea_thai`), Lao (`sea_lao`), Burmese (`sea_burmese`), Khmer (`sea_khmer`), Tibetan (`sea_tibetan`), Georgian (`caucasian_georgian`), and Ethiopic (`african_ethiopic`).
- **Georgian Table Resolution**: Expanded Georgian table prefix matching to `("ka.", "ka-", "ka.utb")` to support custom and alternate Liblouis tables.
- **Submodule Gettext Safety**: Added fallback gettext `_()` initializers in `input_sync.py` and `language_dialogs.py` to prevent `NameError` in headless and standalone environments.
- **Neutral Gap Splitting & Numeric Literals**: Improved neutral gap boundary logic in `segmenter.py` to preserve contiguous numbers atomically rather than slicing digits across script boundaries.
- **Single-Segment Tactile Indicators**: Extended `translator.py` to support `dot8_first` and `dot7_first` pin indicators when translating whole lines in secondary scripts.
- **Path Traversal Protection**: Sanitized Liblouis table file paths with `os.path.basename()` in `translator.py`.
- **Caret Announcement Formatting**: Replaced `.format()` with safe `%s` formatting in `script_announceLanguageAtCaret` to avoid `KeyError` crashes when inspecting literal curly braces (`{` or `}`).
- **Monkey-Patch Idempotency**: Guarded `louisHelper.translate` and `brailleInput.BrailleInputHandler.input` against recursive re-wrapping during plugin reload.
- **Settings Panel Registration Safety**: Protected `NVDASettingsDialog.categoryClasses` against duplicate additions and ensured clean removal on termination.

### Added
- **Sinhala & Armenian Script Registries**: Added complete `ScriptInfo` definitions for `indic_sinhala` (`sin-in-g1.utb`) and `caucasian_armenian` (`hy.ctb`) in `scripts_data.py`.
- **Comprehensive Audit Test Suite**: Added `tests/test_audit_fixes.py` covering type annotations, language mappings, boundary conditions, tactile pins, and lifecycle safety.
- **Python Install Manager Prioritization**: Updated `build.ps1` to detect and prioritize `py.exe` (Python Install Manager) and clean `__pycache__` artifacts during packaging.

---

## [1.0.0] - 2026-09-20

### Added
- Initial release of Auto Braille for NVDA.
- Real-time in-line multi-script Liblouis braille output translation.
- Bi-directional Perkins braille keyboard layout auto-switching.
- Support for Arabic, Persian, Cyrillic, Hebrew, Greek, Indic, East Asian, and Latin writing systems.
- Tactile pin indicators (Dot 8, Dot 7, Dots 7 & 8 underline).
- Document language (`lang`) tag detection with Unicode fallback.
