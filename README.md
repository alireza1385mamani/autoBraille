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

### 4. Smart Document Language Tag Integration (`lang` tags)
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
|                                                                                 |
| Tactile indicator for language boundaries: [Dot 8 under first cell...         v] |
| Primary output braille table:              [Automatic (From NVDA settings)    v] |
| Primary Perkins input braille table:       [Automatic (Match output table)    v] |
|---------------------------------------------------------------------------------|
| Active Secondary Braille Tables (Auto-Detected):                                |
| +-----------------------------------------------------------------------------+ |
| | Persian grade 1 (fa-ir-g1.utb)  —  Input: Persian grade 1                   | |
| | Unified English Braille Grade 2 (en-ueb-g2.ctb)  —  Input: UEB Grade 2      | |
| | Russian literary braille (ru-litbrl.ctb)  —  Input: Russian literary        | |
| +-----------------------------------------------------------------------------+ |
| [&Add Table...]   [&Configure Table...]   [&Remove Table]                       |
+---------------------------------------------------------------------------------+
```

### Adding a Secondary Table
1. Click **Add Table...**.
2. Select any Liblouis braille table (e.g., `fa-ir-g1.utb`, `en-ueb-g2.ctb`, `ru-litbrl.ctb`, `ar-ar-g1.utb`).
3. Auto Braille automatically infers the script, pairs the matching Perkins input table, and configures companion table fallback.
4. Click **OK** &mdash; that's it!

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

Auto Braille commands are available in NVDA's Input Gestures dialog (**`NVDA Menu -> Preferences -> Input Gestures -> Auto Braille`**):

* **Toggles automatic universal multi-script braille translation on and off** (Unassigned by default).
* **Cycles or toggles Perkins braille keyboard input language** (Unassigned by default).
* **Announces the language and braille table at the caret or review cursor** (Recommended: assign to `NVDA + Shift + L` or a key on your braille display).

---

## 🧪 Testing Your Braille Display

Explore the test suites included in the `doc/` directory:
* **Interactive HTML Test Document:** `doc/autoBraille_test_document.html` (open in Chrome, Edge, or Firefox).
* **Plain Text Test Document:** `doc/autoBraille_test_document.txt` (open in Notepad).

---

## 🛠️ Developer Guide & Architecture

Are you interested in how Auto Braille hooks `louisHelper.translate`, manages `b2r`/`r2b` array remapping, safely guards Windows Secure Desktop sessions, or communicates with Windows Win32 keyboard APIs?
Read the comprehensive [Developer Guide](DEVELOPER_GUIDE.md).

### Building from Source

Build the clean `.nvda-addon` bundle into the `dist/` folder using the Python Install Manager:
```bash
py.exe build.py
```
Or with PowerShell on Windows:
```powershell
.\build.ps1
```

### Running Automated Tests

Run the complete 6-part unit test suite covering audit fixes, table resolution, segmentation, tactile indicators, document tags, intra-script disambiguation, and Grade 2 boundary guarding:
```bash
py.exe tests/test_audit_fixes.py
py.exe tests/test_tables_mode.py
py.exe tests/test_features_3_4.py
py.exe tests/test_segmenter.py
py.exe tests/test_intra_script.py
py.exe tests/test_grade2_boundary.py
```
Or run all tests with the PowerShell build script:
```powershell
powershell -ExecutionPolicy Bypass -File build.ps1 -RunTests
```

### Localization & Translations

Auto Braille adheres to standard GNU gettext localization practices:
* All translatable UI strings are preceded by `# Translators:` comments for clarity.
* Regenerate the translation template (`addon/locale/autoBraille.pot`) anytime strings change:
```bash
py.exe generate_pot.py
```

---

## 🤝 Contributing

Contributions, translations, and bug reports are warmly welcomed! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on code style, typing, and pull request workflows.

---

## 📄 License

Auto Braille is licensed under the [GNU General Public License v2.0](LICENSE) (GPL-2.0).
