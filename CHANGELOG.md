# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6] - 2026-09-27

### Added
- **Math & STEM Auto-Detection**:
  - Automatically identifies inline mathematical expressions, equations, and LaTeX delimiters (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`, `f(x) = 2x + 1`, `E = mc^2`, `<=`, `>=`, `!=`, etc.).
  - Dynamically routes formula spans through dedicated math braille tables (e.g., `en-ueb-math.ctb` / Nemeth Code) while keeping surrounding prose in standard literary tables.
  - Currency sign protection: Distinguishes LaTeX math delimiters from monetary amounts (`$50`, `$10.99`).
  - Trailing punctuation shielding: Sentence periods, commas, and semicolons are separated from math spans to avoid syntax corruption.
  - Grade 2 contraction exemption: Math tokens are protected from literary contraction rules.
  - Settings UI toggle and custom math table selector dropdown in Auto Braille settings.
- **Hardware Status Cell Language Indicators**:
  - Renders tactile language indicators on physical status cells for 40-cell, 60-cell, and 80-cell braille displays (Focus, HIMS Braille Edge, Brailliant, Orbit Reader, Alva, etc.).
  - Configurable modes: Off, 2-letter tactile indicator, 1-letter tactile indicator, or Primary/Secondary dot patterns.
  - Displays standard tactile dot codes: `⠢⠝` (`en`), `⠋⠁` (`fa`), `⠙⠑` (`de`), `⠋⠗` (`fr`), `⠍⠁` (`math`), etc.
  - Zero-overhead graceful fallback on displays without status cells (`numStatusCells == 0`).
- **Application-Specific & Profile-Aware Braille Switching**:
  - Automatically hooks `config.post_configProfileSwitch` to react instantly when switching NVDA configuration profiles or app triggers (e.g., Visual Studio, Word, terminal).
  - Automatically clears translation caches, invalidates active tables, and re-renders braille on active displays immediately.
- **Custom User Lexicon / Dictionary Overrides**:
  - Allows users to define custom word- or symbol-specific braille routing rules via an intuitive GUI dialog (`CustomDictionaryDialog` & `EditCustomEntryDialog`).
  - Supports custom table assignment and case-sensitivity per entry.
  - Atomic word-boundary locked (`\b`) pre-partitioning before literary and math segmenters.
- **Unassigned Braille Display Key Shortcuts / Chords**:
  - Added new scripts to the `"Auto Braille"` NVDA Input Gestures category:
    - `script_cycleSecondaryTable`: Rapidly cycle through secondary braille tables directly from the display.
    - `script_cyclePrimaryTable`: Cycle through primary braille tables.
    - `script_toggleMathDetection`: Instantly toggle Math & STEM auto-detection on/off.
  - Left completely unassigned out-of-the-box to give users 100% freedom to map custom braille keys/chords without conflicting with existing display commands.
- **Community Invitation & Hardware Testing Notice**:
  - Verified on the HIMS Braille Edge 40 display; community testing on other refreshable braille displays is warmly invited.
  - Documented as an open proof of concept for the international blind community, welcoming native readers of other languages to contribute.
  - Roadmap section updated to reflect single-author status ("I" instead of "we").
- **Dedicated Test Suite & Test Runner Expansion**:
  - Added `tests/test_new_features.py` with 17 rigorous test cases covering all 5 new areas.
  - Expanded `run_tests.py` to 9 comprehensive suites with 100% pass rate.

---

## [1.0.5] - 2026-09-27

### Added
- **Full Latin-Script Sub-Language Diacritic Detection**:
  - Automatically identifies and routes language-exclusive Latin letters and diacritics across European and Latin-alphabet languages:
    - **German**: `ä, ö, ü, ß` &rarr; routes to German braille (`de-g1.ctb` / `de-g2.ctb`).
    - **French**: `é, è, ê, ç, œ` &rarr; routes to French braille (`fr-bfu-comp8.ctb`).
    - **Turkish**: `ğ, ş, ı, İ` &rarr; routes to Turkish braille (`tr-g1.ctb`).
    - **Spanish**: `ñ, ¿, ¡` &rarr; routes to Spanish braille (`es-g1.ctb`).
    - **Scandinavian**: `å, æ, ø` &rarr; routes to Danish (`da-dk-g1.ctb`), Swedish, or Norwegian braille.
    - **Polish & Czech/Slovak**: `ą, ę, ł, ń, ś, ź, ż, ć` & `ř, ů, ť, ď, ň, ž, š, č, ě`.
  - **Atomic Word-Level Locking**: Words like `Kühlschrank` or `français` are never sliced into letter fragments; the entire word is routed as an indivisible token with correct braille contractions.
  - **Sub-Microsecond ASCII Fast Path**: Pure 7-bit ASCII English prose skips diacritic classification completely via C-level regex `has_non_ascii_latin()` in under 0.35 µs, ensuring zero latency during rapid braille scrolling.
  - **English Loanword Anchoring**: Common accented English words (`café`, `résumé`, `cliché`, `façade`, `fiancé`, etc.) stay in English UEB unless the sentence contains foreign stop words indicating a foreign clause (e.g. `Wir treffen uns im Café`).
  - **Turkish Dotless "i" Case-Folding Safety**: Uses explicit codepoint matching (`[ğĞıİşŞ]`) avoiding `str.lower()` which corrupts Turkish dotless `ı` and dotted `İ`.
  - **3-Tier Shared Diacritic Disambiguation**: Multi-candidate shared diacritics (e.g. `ä, ö, ü` in German vs Turkish) resolve via exclusive letters first, clause context density second, and language-characteristic n-grams (`sch` vs `lar`) third.
  - **Settings UI Control**: Added `"Automatically detect European language diacritics in Latin text (e.g. German, French, Spanish, Turkish)"` checkbox in Auto Braille settings with full gettext translation.
  - **Dedicated Test Suite**: Added `tests/test_latin_sub_languages.py` covering all 8 verification areas with 100% pass rate.
  - **Test Runner Expansion**: Expanded `run_tests.py` to an 8-suite test framework with dynamic suite counting.

---

## [1.0.4] - 2026-09-26

### Added
- **Python 3.14 Default Build & Test Target**:
  - Full native verification and support for Python 3.14+ (tested and verified on Python 3.14.7) while maintaining 100% backward-compatibility with NVDA 2024 LTS (Python 3.11).
  - PEP 649 / PEP 749 deferred annotation evaluation compatibility across all modules with `from __future__ import annotations`.
  - Added official `pyproject.toml` with PEP 621 project metadata declaring `requires-python = ">=3.11, <3.15"` and classifiers for Python 3.11, 3.12, 3.13, and 3.14.
- **Unified Single-Command Test Runner (`run_tests.py`)**:
  - Added a standalone test runner executing bytecode pre-compilation checks and all 7 test suites in isolated subprocesses using the active Python interpreter in ~0.45s.
  - Guarantees zero cross-suite mock pollution and clean stdout/stderr reporting.
- **Pre-Build Bytecode Compilation Verification**:
  - Integrated `verify_compilation()` in `build.py` to compile all Python modules with `py_compile.compile(..., doraise=True)` prior to packaging `.nvda-addon` bundles.
- **Multi-Version GitHub Actions CI Matrix**:
  - Configured test workflows across Python 3.14 (primary) and Python 3.11 (NVDA LTS) in `.github/workflows/release.yml`.

### Changed & Security Hardening
- **64-bit ctypes Signatures**: Declared explicit `argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.LPWSTR, wintypes.INT]` and `restype = wintypes.INT` for `kernel32.GetLocaleInfoW` in `input_sync.py` to eliminate 64-bit calling convention ambiguities.
- **Unified Table Language Prefix Matching**: Refactored `resolve_input_table_for_lang()` in `input_sync.py` to use `scripts_data.get_table_lang_code()`, correctly matching dotted tables (e.g. `el.ctb`, `syc.utb`, `he.ctb`) as well as hyphenated tables (`fa-ir-g1.utb`, `en-ueb-g1.ctb`).
- **PowerShell Script Hardening (`build.ps1`)**: Prioritized `python.exe` over `py.exe` to eliminate access-denied errors from Windows App execution aliases, and integrated directly with `run_tests.py`.

---

## [1.0.3] - 2026-09-26

### Added
- **Contracted Braille (Grade 2) Support & Boundary Guarding**:
  - Full Grade 2 output support with automatic companion Grade 1 fallback mapping (`GRADE2_COMPANION_MAP`) across English (UEB), Arabic, German, French, Spanish, Russian, and more.
  - **Single-Letter Wordsign Protection**: Isolated letters (such as `b` in `گزینه b`, or in lists/formulas) are guarded from incorrectly expanding to whole-word contractions (e.g., `but` in UEB).
  - **Technical Syntax & Code Identifier Shielding**: Automatically detects variable names, `snake_case`, `camelCase`, and technical syntax (`user_id`, `print()`), routing them to uncontracted Grade 1 to prevent syntax corruption.
  - **Numeric Boundary Bleed Prevention**: Inspects prefix context to guarantee adjacent numbers (`123b`) do not bleed into numeric mode contraction anomalies.
  - **Settings UI Control**: Configurable "Guard Grade 2 contracted braille at script boundaries and isolated words" checkbox in Auto Braille settings with complete gettext localization.
  - **Comprehensive Test Suite**: Added `tests/test_grade2_boundary.py` with 100% pass coverage across wordsigns, code tokens, companion lookups, and translation engine integration.
- **3-Tier Multi-Language Architecture & Intra-Script Disambiguation**:
  - Solved intra-script conflicts for shared scripts (Persian vs Arabic in Arabic script, Ukrainian/Belarusian vs Russian in Cyrillic, Urdu/Kurdish).
  - Implemented 3-tier disambiguation: Document tags (Tier 1) &rarr; Exclusive lexical marker scoring (Tier 2) &rarr; Character n-gram frequency fallback (Tier 3).
  - Added dedicated test suite `tests/test_intra_script.py`.
- **One-Click Setup Wizard (Auto-Detect Windows Keyboards)**:
  - Added automatic in-memory Win32 detection (`GetKeyboardLayoutList`) and read-only registry preload discovery (`HKCU\Keyboard Layout\Preload`) with strict hex validation.
  - Implemented 3-tier dialect fallback and automatic deduplication across regional Windows keyboard layouts (e.g. US/UK English, Saudi/Egyptian Arabic).
  - Preserves user primary language and filters out already-configured tables.
  - Added accessible `AutoDetectWizardDialog` with an **"Edit Table..."** button allowing users to customize candidate output and Perkins input tables before adding them.
  - Added `tests/test_auto_detect_keyboards.py` unit test suite covering 64-bit ctypes prototypes, registry security, dialect deduplication, catalog validation, and UI lifecycle.

### Changed
- **Developer Test Suite Renaming**: Renamed legacy test file `tests/test_features_3_4.py` to `tests/test_doc_lang_and_tactile.py` for clarity, self-documentation, and maintainability across the testing pipeline, CI workflows, and developer documentation.

---

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
