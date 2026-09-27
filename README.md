# Auto Braille for NVDA

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](LICENSE)
[![NVDA Compatibility](https://img.shields.io/badge/NVDA-2024.1%20to%202026.3%2B-green.svg)](https://www.nvaccess.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-lightgrey.svg)](https://microsoft.com)

**Auto Braille** is a high-performance NVDA add-on that brings universal **in-line multi-script braille output translation** and **intelligent Perkins keyboard input auto-switching** to every refreshable braille display supported by NVDA.

---

## 🌟 Why Auto Braille?

Traditionally, NVDA users can only select a single braille translation table at a time. When reading mixed-language texts (such as Persian or Russian with embedded English technical terms), foreign words appear garbled or mis-translated. Furthermore, typing on a braille display's Perkins keyboard requires cumbersome manual menu trips whenever switching between languages.

**Auto Braille solves this completely:**
* **Read seamlessly:** Auto Braille dynamically identifies language scripts within any sentence and renders each word with its dedicated Liblouis braille table (e.g. Persian `fa-ir-g1.utb` alongside English `en-ueb-g1.ctb`).
* **Type effortlessly:** Switch your Windows keyboard layout with `Alt + Shift` or `Windows + Space`, and your braille display's Perkins keyboard updates its input table instantly in real time!
* **Feel language transitions:** Optional tactile indicators (such as Dot 8 on the transition cell or continuous Dots 7 & 8 underline under secondary language text) let you feel language changes without interrupting your reading flow.
* **Document language tag integration:** In web browsers and Microsoft Word / LibreOffice, official `lang` attributes (e.g. `<span lang="fa">`) are honored, complete with automatic character validation and fallback.

---

## 🚀 Key Features

### 1. Universal In-Line Multi-Script Translation
* Supports **24+ global writing systems**: Arabic, Persian, Urdu, Kurdish, Cyrillic (Russian, Ukrainian, etc.), Hebrew, Greek, South Asian / Indic (Hindi, Tamil, Bengali, etc.), East Asian CJK (Chinese, Japanese, Korean), Southeast Asian (Thai, Burmese, Khmer, Tibetan), Caucasian (Georgian, Armenian), and Latin.
* Pixel-perfect Liblouis cursor routing: pressing any cursor routing key navigates directly to the exact source character under your finger.
* Microsecond-level performance with zero lag during rapid scrolling.

### 2. Bi-Directional Perkins Input Auto-Switching
* Real-time synchronization between the active Windows keyboard layout (LANGID) and NVDA's Perkins braille input table.
* Typing in Persian, English, Russian, or any active language requires zero manual configuration.

### 3. Tactile & Spoken Boundary Indicators (Optional)
* **Dot 8 under first cell of language change:** Raises bottom-right pin 8 on the first cell of a language transition.
* **Dot 7 under first cell of language change:** Raises bottom-left pin 7 on the first cell of a language transition.
* **Dots 7 and 8 underline:** Continuously underlines secondary language text with pins 7 and 8.
* **Announce Language at Caret:** Press a gesture to simultaneously speak aloud and flash the active character, writing system, and Liblouis table on your braille display!

### 4. Full Latin-Script Sub-Language Diacritic Detection
* **Automatic Diacritic Routing:** Recognizes language-exclusive Latin letters and diacritics across European languages:
  - **German:** `ä`, `ö`, `ü`, `ß` &rarr; automatically invokes German braille (`de-g1.ctb` / `de-g2.ctb`).
  - **French:** `é`, `è`, `ê`, `ç`, `œ` &rarr; automatically invokes French braille (`fr-bfu-comp8.ctb`).
  - **Turkish:** `ğ`, `ş`, `ı`, `İ` &rarr; automatically invokes Turkish braille (`tr-g1.ctb`).
  - **Spanish:** `ñ`, `¿`, `¡` &rarr; automatically invokes Spanish braille (`es-g1.ctb`).
  - **Scandinavian:** `å`, `æ`, `ø` &rarr; automatically invokes Danish (`da-dk-g1.ctb`), Swedish, or Norwegian braille.
  - **Polish & Czech/Slovak:** `ą, ę, ł, ń, ś, ź, ż, ć` & `ř, ů, ť, ď, ň, ž, š, č, ě`.
* **Atomic Word-Level Locking:** Words like `Kühlschrank` or `français` are never sliced mid-word; the entire word routes as an indivisible token with correct braille contractions.
* **Sub-Microsecond ASCII Fast Path:** Pure 7-bit ASCII English text bypasses diacritic classification in `< 0.35 µs`, ensuring zero latency during rapid scrolling.
* **English Loanword Anchoring:** Common accented English words (`café`, `résumé`, `cliché`, `façade`, `fiancé`) stay in English UEB unless surrounding context contains foreign stop words.
* **Turkish Dotless "i" Case-Folding Safety:** Codepoints `[ğĞıİşŞ]` are preserved without case-folding corruption.

### 5. Math & STEM Auto-Detection (LaTeX & Technical Formulas)
* **LaTeX Formula Recognition:** Automatically recognizes inline LaTeX mathematical notation (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`) and dynamically routes formulas through dedicated technical math tables (such as Unified English Braille Technical Math `en-ueb-math.ctb` or Nemeth Code `nemeth.ctb`).
* **Plain-Text Equation Parsing:** Recognizes inline mathematical expressions (`f(x) = 2x + 1`, `E = mc^2`, `a + b = c`, `y = mx + b`, `x <= 10`, `\sqrt{x}`, `\frac{a}{b}`) while keeping surrounding literary prose in standard literary braille.
* **Currency Collision Prevention:** Currency values like `$50`, `$10.99`, or `$100.00` are strictly guarded and never misidentified as LaTeX math formulas.
* **Sentence Punctuation Detachment:** Trailing sentence punctuation (periods, commas, colons, question marks) is detached from the formula boundary so sentence punctuation remains in literary braille.
* **Grade 2 Protection:** Technical math expressions are excluded from Grade 2 contracted word-sign substitutions.

### 6. Hardware Status Cell Language Indicators
* **Tactile 2-Letter Language Codes:** Many 40-cell, 60-cell, and 80-cell braille displays (Focus, Braille Edge, Brailliant, Orbit Reader) have 2 to 4 physical **status cells** separated from the main reading line. Auto Braille displays a 2-letter tactile language indicator:
  - `⠢⠝` (`en`): English / Latin
  - `⠋⠁` (`fa`): Persian
  - `⠙⠑` (`de`): German
  - `⠋⠗` (`fr`): French
  - `⠗⠥` (`ru`): Russian
  - `⠑⠎` (`es`): Spanish
  - `⠍⠁` (`ma`): Math & STEM formula
* **Configurable Modes:**
  - **Disabled:** Leaves status cells to NVDA's default behavior.
  - **Current language at cursor:** Dynamically updates the status cells as you read across languages and formulas.
  - **Primary braille language:** Always displays the base language indicator.
* **Hardware Safety:** Fully guarded with display cell count checks; portable displays with 0 status cells gracefully skip without errors.

### 7. App-Specific & Profile-Aware Braille Switching
* **NVDA Profile Integration:** Hooks into NVDA's configuration profile lifecycle (`config.post_configProfileSwitch`).
* When switching between applications (e.g. VS Code with Nemeth/technical math vs. Microsoft Word with Grade 2 contracted literary braille), Auto Braille automatically invalidates internal caches, synchronizes Perkins input tables, and refreshes the braille display.

### 8. Custom User Lexicon / Dictionary Overrides
* **Word-to-Table Custom Rules:** Define custom word or phrase overrides in NVDA Settings to force specific vocabulary to always translate with a chosen braille table (e.g. `Python` &rarr; `en-ueb-g2.ctb`, or `LaTeX` &rarr; `en-ueb-math.ctb`).
* **Word Boundary Locking:** Enforces atomic word boundaries (`r"(?<!\w)...(?!\w)"`) to prevent partial substring corruption (e.g. matching `in` will never corrupt `morning` or `terminal`).
* **Case Sensitivity Options:** Each custom entry can be configured as case-sensitive or case-insensitive.
* **Accessible Management Dialog:** Add, edit, and remove custom rules with keyboard navigation and instant preview.

### 9. Direct Braille Display Key Shortcuts / Chords (Unassigned Gestures)
* **Customizable Braille Display Binding:** Auto Braille scripts are registered with **unassigned gestures** in NVDA's Input Gestures dialog under the **Auto Braille** category.
* Users can map any key, rocker switch, thumb key, or Perkins chord on their braille display (e.g. `Space + Dot 1 + Dot 2`) without collisions with existing display driver shortcuts!

### 10. Smart Document Language Tag Integration (`lang` tags)
* Automatically detects HTML and document language tags (`<span lang="fa">`, `<p lang="en">`).
* **Conflict Validator:** If an author mistakenly tags Persian text as English, Auto Braille automatically validates the characters and falls back to Unicode script detection so text is never corrupted.

---

## 📦 Installation

1. Download the latest **`autoBraille-X.X.X.nvda-addon`** package from the [Releases](https://github.com/alireza1385mamani/autoBraille/releases) page.
2. Open the downloaded file in NVDA (or press `Enter` on the file in File Explorer).
3. When NVDA asks to confirm installation, select **Yes**.
4. Restart NVDA when prompted.

---

## ⚙️ Configuration

Open NVDA Settings (**`NVDA + Control + G`**) and navigate to the **Auto Braille** category:

```
+---------------------------------------------------------------------------------+
| Auto Braille Settings                                                           |
+---------------------------------------------------------------------------------+
| [X] Enable automatic multi-language braille output translation                  |
| [X] Automatically sync Perkins braille input with active Windows keyboard layout|
| [X] Honor document language tags in web and office documents (e.g. HTML, Word)  |
| [X] Protect isolated letters and code identifiers in Contracted Braille (G2)    |
| [X] Automatically detect European language diacritics in Latin text             |
| [X] Automatically detect Math and STEM formulas (e.g. LaTeX, equations)         |
|                                                                                 |
| Tactile indicator for language boundaries: [Dot 8 under first cell...         v] |
| Hardware status cell language indicator:   [Current language at cursor        v] |
| Primary output braille table:              [Automatic (From NVDA settings)    v] |
| Math braille table:                        [Unified English Braille - Math    v] |
| Primary Perkins input braille table:       [Automatic (Match output table)    v] |
|---------------------------------------------------------------------------------|
| Active Secondary Braille Tables (Auto-Detected):                                |
| +-----------------------------------------------------------------------------+ |
| | German grade 1 (de-g1.ctb)  —  Input: German grade 1                        | |
| | Persian grade 1 (fa-ir-g1.utb)  —  Input: Persian grade 1                   | |
| | French computer 8-dot (fr-bfu-comp8.ctb)  —  Input: French computer 8-dot   | |
| | Turkish grade 1 (tr-g1.ctb)  —  Input: Turkish grade 1                      | |
| +-----------------------------------------------------------------------------+ |
| [&Add Table...] [&Configure Table...] [&Remove Table] [&Auto-Detect...] [&Custom Dictionary...] |
+---------------------------------------------------------------------------------+
```

### Adding a Secondary Table
1. Click **Add Table...** or click **Auto-Detect Keyboards...** to instantly configure all installed Windows keyboard languages.
2. If adding manually, select any Liblouis braille table (e.g., `fa-ir-g1.utb`, `en-ueb-g2.ctb`, `ru-litbrl.ctb`, `ar-ar-g1.utb`).
3. Auto Braille automatically infers the script, pairs the matching Perkins input table, and configures companion table fallback.
4. Click **OK** &mdash; that's it!

### ⚡ One-Click Setup Wizard (Auto-Detect Windows Keyboards)
* **Instant Automatic Configuration:** Click **Auto-Detect Keyboards...** in settings to scan Windows for all installed keyboard languages (e.g. Persian, Arabic, Russian, English, French, German).
* **Smart Liblouis Mapping:** Auto Braille resolves each layout to its optimal braille output table and Perkins input table, while preserving your primary language and preventing duplicate entries.
* **Preview & In-Place Customization:** An accessible preview dialog displays all detected languages. Highlight any language and click **Edit Table...** to customize its output or Perkins input table before applying!

### 🌟 Contracted Braille (Grade 2) & Boundary Guarding
* **No Accidental Contractions:** In UEB Grade 2, isolated single letters contract to whole words (`b` = "but", `c` = "can", `x` = "it"). Auto Braille automatically guards single letters in mixed text (e.g. `گزینه b`, `کلید c`), routing them through uncontracted Grade 1 companion tables so words like `but` never appear by mistake!
* **Code & Identifier Protection:** Variables and technical code (e.g. `user_id`, `file_name`, `camelCase`, file paths) are protected against literary contractions.
* **Numeric Boundary Lookback:** Letters immediately following digits (e.g. `123b`) are protected from numeric bleeding.

### 🌐 3-Tier Multi-Language Architecture
* **Tier 1 (Cross-Script):** 100% deterministic Unicode script segmentation across all global alphabets.
* **Tier 2 (Loanword Absorption):** Persian words with Arabic letters (`دایرة‌المعارف`, `نهایة`, `خاصةً`) and English words with accents (`café`, `résumé`, `über`) stay in their native table with zero flapping.
* **Tier 3 (Intra-Script Disambiguation):** Automatically distinguishes between languages using the same alphabet (Persian vs. Arabic; English vs. French/German) using document language markup (`lang="ar"`), Windows keyboard layouts, and grammatical stop-word phrase density.
* **Non-Latin Primary Defaults:** Persian, Arabic, and Russian primary users automatically get English UEB as their secondary table out of the box!

---

## ⌨️ Input Gestures

Auto Braille commands are registered with **unassigned gestures** in NVDA's Input Gestures dialog (**`NVDA Menu -> Preferences -> Input Gestures -> Auto Braille`**). Users can map them to any preferred braille display key, thumb key, Perkins chord, or keyboard shortcut:

* **Cycles through active secondary braille tables** (Unassigned by default).
* **Cycles primary braille table between configured languages** (Unassigned by default).
* **Toggles automatic Math and STEM formula detection on and off** (Unassigned by default).
* **Toggles automatic universal multi-script braille translation on and off** (Unassigned by default).
* **Cycles or toggles Perkins braille keyboard input language** (Unassigned by default).
* **Announces the language and braille table at the caret or review cursor** (Recommended: assign to `NVDA + Shift + L` or a key on your braille display).

---

## 🧪 Hardware Testing & Community Invitation

> [!IMPORTANT]
> **Tested Hardware Display:** I have personally tested this add-on extensively with the **Braille Edge 40 by HIMS**.
> Because braille displays differ across manufacturers in key layouts, driver implementations, and physical status cells (e.g. Focus 40/80, Brailliant BI, Orbit Reader, Alva, PAC Mate), comprehensive testing across all refreshable braille displays is warmly encouraged!
>
> This project serves as an open-source proof of concept, and anyone who wants to build on it, extend it, or integrate new tables is very welcome to do so. Since I am not an expert in languages other than Persian and English, feedback, bug reports, and testing from native braille readers in French, German, Spanish, Turkish, Arabic, Russian, Indic, and other languages are deeply appreciated.

Explore the test suites included in the `doc/` directory:
* **Interactive HTML Test Document:** `doc/autoBraille_test_document.html` (open in Chrome, Edge, or Firefox).
* **Plain Text Test Document:** `doc/autoBraille_test_document.txt` (open in Notepad).

---

## 🛠️ Developer Guide & Architecture

Are you interested in how Auto Braille hooks `louisHelper.translate`, manages `b2r`/`r2b` array remapping, safely guards Windows Secure Desktop sessions, or communicates with Windows Win32 keyboard APIs?
Read the comprehensive [Developer Guide](DEVELOPER_GUIDE.md).

### Python Version & Environment Compatibility

Auto Braille is developed, compiled, and tested against **Python 3.14+ by default**, while maintaining full backward-compatibility with NVDA's Python 3.11 runtime environment.

### Building from Source

Build the clean `.nvda-addon` bundle into the `dist/` folder (includes automatic pre-build bytecode compilation verification):
```bash
python build.py
```
Or with PowerShell on Windows:
```powershell
.\build.ps1
```

### Running Automated Tests

Run the complete 9-part unit test suite covering audit fixes, table resolution, segmentation, tactile indicators, document tags, intra-script disambiguation, Grade 2 boundary guarding, Windows keyboard auto-detection, Latin sub-language diacritics, Math & STEM auto-detection, and hardware status cells with a single command:
```bash
python run_tests.py
```
Or with the PowerShell build script:
```powershell
powershell -ExecutionPolicy Bypass -File build.ps1 -RunTests
```

Individual test suites can also be run directly:
```bash
python tests/test_audit_fixes.py
python tests/test_tables_mode.py
python tests/test_doc_lang_and_tactile.py
python tests/test_segmenter.py
python tests/test_intra_script.py
python tests/test_grade2_boundary.py
python tests/test_auto_detect_keyboards.py
python tests/test_latin_sub_languages.py
python tests/test_new_features.py
```

### Localization & Translations

Auto Braille adheres to standard GNU gettext localization practices:
* All translatable UI strings are preceded by `# Translators:` comments for clarity.
* Regenerate the translation template (`addon/locale/autoBraille.pot`) anytime strings change:
```bash
py.exe generate_pot.py
```

---

## 🗺️ Roadmap & Future Work

As the author of Auto Braille, I am continually working to make braille reading and typing on NVDA as fluid and natural as possible across all languages and displays. Future explorations include:
* **Expanded STEM notation support:** Richer MathML and advanced LaTeX expression handling.
* **Intra-word multi-language code-switching:** Further refinements for technical programming languages and mixed bilingual jargon.
* **Per-application braille profiles UI:** Even deeper integration with NVDA application profiles directly from the Auto Braille settings dialog.
* **Community-submitted language tables:** Pre-configured table sets for specialized regional braille standards.

---

## 🤝 Contributing

Contributions, translations, and bug reports are warmly welcomed! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on code style, typing, and pull request workflows.

---

## 📄 License

Auto Braille is licensed under the [GNU General Public License v2.0](LICENSE) (GPL-2.0).
