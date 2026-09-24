# Auto Braille: Universal Multi-Script In-Line Translation & Perkins Input for NVDA

* **Author:** Alireza Mamani & Antigravity (<https://github.com/alireza1385mamani>)
* **Repository:** <https://github.com/alireza1385mamani/autoBraille>
* **NVDA Compatibility:** NVDA 2024.1 to 2026.3+
* **License:** GNU General Public License v2.0 (GPL-2.0)

**Auto Braille** is an open-source NVDA global plugin that brings seamless multi-lingual braille output and intelligent Perkins keyboard input auto-switching to every refreshable braille display supported by NVDA.

---

## Key Features

### 1. In-Line Multi-Script Output Translation
* Automatically identifies distinct writing systems (Arabic/Persian, Cyrillic, Hebrew, Greek, South Asian / Indic, East Asian CJK, Southeast Asian, and Latin) within any text line.
* Dynamically translates each language segment using its dedicated Liblouis braille table (e.g. `fa-ir-g1.utb` for Persian and `en-ueb-g1.ctb` for English).
* Stitches braille cells together seamlessly with microsecond-level performance and full cursor routing accuracy.

### 2. Bi-Directional Perkins Braille Keyboard Auto-Switching
* Real-time synchronization between the active Windows keyboard layout (e.g. Persian `0x0429` vs. English `0x0409`) and the Perkins braille input table.
* Press `Alt + Shift` or `Windows + Space` on your computer or braille display to switch languages &mdash; your Perkins braille keyboard updates instantly without opening any menus!

### 3. Tactile & Spoken Boundary Indicators (Optional)
* **Tactile Pin Indicators:** On 8-dot braille displays, subtly feel language transitions:
  * **Dot 8 under first cell of language change (Recommended):** Raises bottom-right pin 8 on the first cell of a language switch.
  * **Dot 7 under first cell of language change:** Raises bottom-left pin 7 on the first cell of a language switch.
  * **Dots 7 and 8 underline under secondary language cells:** Continuously underlines secondary language text.
* **Announce Language at Caret:** Press your assigned shortcut to hear and feel the active character, writing system, and Liblouis table name simultaneously spoken and flashed in braille.

### 4. Smart Document Language Tag Integration (`lang` tags)
* In web browsers (Chrome, Edge, Firefox) and Office suites (Word, LibreOffice), official document language tags (`<span lang="fa">`, `<p lang="en">`) are automatically detected and respected.
* **Automatic Script Compatibility Validation:** If text is marked with an incorrect language tag, Auto Braille automatically validates the characters and falls back to the Unicode script detector so text is never garbled!

---

## Configuration

Open NVDA Settings (**`NVDA + Control + G`**) and navigate to the **Auto Braille** category:

1. **Enable automatic multi-language braille output translation:** Master toggle for in-line multi-script translation.
2. **Automatically sync Perkins braille input with active Windows keyboard layout:** Master toggle for real-time Perkins input table switching.
3. **Honor document language tags in web and office documents:** Prioritize official HTML/Word `lang` tags when accurate.
4. **Tactile indicator for language boundaries:** Choose between *None*, *Dot 8 under first cell*, *Dot 7 under first cell*, or *Dots 7 and 8 underline*.
5. **Primary output braille table:** Select your default output table from all installed Liblouis tables, or choose *Automatic (Use active NVDA output table)*.
6. **Primary Perkins input braille table:** Select your default input table, or choose *Automatic (Follow active NVDA input table)*.
7. **Active Secondary Braille Tables List:** Click **Add Table...** to activate any secondary braille table (e.g. `fa-ir-g1.utb`, `ru-litbrl.ctb`, `he-IL.utb`). Auto Braille automatically infers the script and pairs the matching Perkins input table.

---

## Input Gestures

Auto Braille exposes commands under the **Auto Braille** category in NVDA's Input Gestures dialog (**`NVDA Menu -> Preferences -> Input Gestures -> Auto Braille`**):

* **Toggles automatic universal multi-script braille translation on and off** (Unassigned by default).
* **Cycles or toggles Perkins braille keyboard input language** (Unassigned by default).
* **Announces the language and braille table at the caret or review cursor** (Recommended shortcut: `NVDA + Shift + L` or a key on your braille display).

---

## Feedback & Contributions

Contributions, bug reports, and pull requests are warmly welcomed on GitHub!
See the Developer Guide and Contributing guidelines in the repository for details on extending tables, scripts, and unit tests.
