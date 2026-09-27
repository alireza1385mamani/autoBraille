# coding: utf-8
"""Comprehensive verification test suite for Latin-Script Sub-Language Diacritic Detection in Auto Braille.

Guarantees:
1. Sub-microsecond pure ASCII fast-path performance (< 0.5 µs per check).
2. Atomic word-level locking (German 'Kühlschrank' and French 'français' never sliced mid-word).
3. English loanword anchoring (accents in 'café', 'résumé' stay in UEB in English sentences).
4. Turkish dotless 'ı' and dotted 'İ' case-folding safety (codepoint preservation).
5. Spanish ('ñ, ¿, ¡') and Scandinavian ('å, æ, ø') diacritic routing.
6. Shared diacritic disambiguation (exclusive letters, context density, language n-grams).
7. End-to-end multi_script_translate with cursor routing (b2r/r2b) and tactile indicators.
"""

import os
import sys
import time
import types
from typing import List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
	sys.stdout.reconfigure(encoding="utf-8", errors="replace")
	sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add add-on path to sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
addon_dir = os.path.join(repo_root, "addon", "globalPlugins")
if addon_dir not in sys.path:
	sys.path.insert(0, addon_dir)

import builtins
builtins._ = lambda s: s

config_mock = types.ModuleType("config")
class DummyConf(dict):
	spec = {}
	def __init__(self):
		super().__init__()
		self["autoBraille"] = {
			"enabled": True,
			"primaryTable": "en-ueb-g1.ctb",
			"primaryInputTable": "en-ueb-g1.ctb",
			"activeTables": "en-ueb-g1.ctb, de-g1.ctb, fr-bfu-comp8.ctb, tr-g1.ctb, es-g1.ctb",
			"autoSyncInputTable": True,
			"honorDocumentLang": True,
			"tactileMarker": "dot8_first",
			"grade2BoundaryGuard": True,
			"detectLatinSubLanguages": True,
		}
		self["braille"] = {
			"translationTable": "en-ueb-g1.ctb",
			"inputTable": "en-ueb-g1.ctb",
		}
config_mock.conf = DummyConf()
sys.modules["config"] = config_mock

braille_mock = types.ModuleType("braille")
braille_mock.TABLES_DIR = r"C:\fake\tables"

class DummyTable:
	def __init__(self, fn: str, dn: str, o: bool = True, i: bool = True):
		self.fileName = fn
		self.displayName = dn
		self.output = o
		self.input = i

braille_tables_mock = types.ModuleType("brailleTables")
braille_tables_mock.TABLES_DIR = r"C:\fake\tables"
braille_tables_mock._tablesDirs = {"app": r"C:\fake\tables"}
braille_tables_mock.listTables = lambda: [
	DummyTable("en-ueb-g1.ctb", "English (Unified) Grade 1"),
	DummyTable("en-ueb-g2.ctb", "English (Unified) Grade 2"),
	DummyTable("de-g1.ctb", "German Grade 1"),
	DummyTable("de-g2.ctb", "German Grade 2"),
	DummyTable("fr-bfu-comp8.ctb", "French Computer 8-dot"),
	DummyTable("tr-g1.ctb", "Turkish Grade 1"),
	DummyTable("es-g1.ctb", "Spanish Grade 1"),
	DummyTable("da-dk-g1.ctb", "Danish Grade 1"),
	DummyTable("fa-ir-g1.utb", "Persian Grade 1"),
	DummyTable("braille-patterns.cti", "Unicode Braille Patterns", False, False),
]
sys.modules["braille"] = braille_mock
sys.modules["brailleTables"] = braille_tables_mock

addonHandler_mock = types.ModuleType("addonHandler")
addonHandler_mock.initTranslation = lambda: None
addonHandler_mock._ = lambda s: s
sys.modules["addonHandler"] = addonHandler_mock

globalPluginHandler_mock = types.ModuleType("globalPluginHandler")
class GlobalPlugin:
	def terminate(self): pass
globalPluginHandler_mock.GlobalPlugin = GlobalPlugin
sys.modules["globalPluginHandler"] = globalPluginHandler_mock

# Mock Liblouis translation engine
louis_mock = types.ModuleType("louis")
def dummy_louis_translate(tableList, inbuf, typeform=None, mode=0, cursorPos=None):
	n = len(inbuf)
	cells = [ord(c) % 256 for c in inbuf]
	b2r = list(range(n))
	r2b = list(range(n))
	cur = cursorPos if cursorPos is not None and 0 <= cursorPos <= n else None
	return cells, b2r, r2b, cur

louis_mock.translate = dummy_louis_translate
sys.modules["louis"] = louis_mock

louisHelper_mock = types.ModuleType("louisHelper")
louisHelper_mock.translate = dummy_louis_translate
sys.modules["louisHelper"] = louisHelper_mock

logHandler_mock = types.ModuleType("logHandler")
class DummyLog:
	def debug(self, *a, **k): pass
	def info(self, *a, **k): pass
	def warning(self, *a, **k): pass
	def error(self, *a, **k): pass
logHandler_mock.log = DummyLog()
sys.modules["logHandler"] = logHandler_mock

scriptHandler_mock = types.ModuleType("scriptHandler")
scriptHandler_mock.script = lambda **kwargs: (lambda f: f)
sys.modules["scriptHandler"] = scriptHandler_mock

ui_mock = types.ModuleType("ui")
ui_mock.message = lambda msg: None
sys.modules["ui"] = ui_mock

api_mock = types.ModuleType("api")
api_mock.getFocusObject = lambda: None
api_mock.getReviewPosition = lambda: None
sys.modules["api"] = api_mock

brailleInput_mock = types.ModuleType("brailleInput")
class MockBrailleInputHandler:
	@classmethod
	def input(cls, *a, **k): pass
brailleInput_mock.BrailleInputHandler = MockBrailleInputHandler
brailleInput_mock.handler = types.SimpleNamespace(table=DummyTable("en-ueb-g1.ctb", "English"))
sys.modules["brailleInput"] = brailleInput_mock

wx_mock = types.ModuleType("wx")
wx_mock.Dialog = object
wx_mock.Sizer = object
wx_mock.BoxSizer = object
wx_mock.CheckBox = object
wx_mock.Choice = object
wx_mock.StaticLine = object
wx_mock.StaticText = object
wx_mock.ListBox = object
wx_mock.Button = object
wx_mock.VERTICAL = 1
wx_mock.HORIZONTAL = 2
wx_mock.ALL = 1
wx_mock.EXPAND = 2
wx_mock.RIGHT = 1
wx_mock.LB_SINGLE = 1
wx_mock.OK = 4
wx_mock.CANCEL = 8
wx_mock.ID_OK = 4
wx_mock.ID_CANCEL = 8
sys.modules["wx"] = wx_mock

gui_mock = types.ModuleType("gui")
gui_mock.guiHelper = types.SimpleNamespace(BoxSizerHelper=object)
gui_mock.messageBox = lambda *a, **k: None
gui_mock.settingsDialogs = types.SimpleNamespace(SettingsPanel=object, NVDASettingsDialog=types.SimpleNamespace(categoryClasses=[]))
sys.modules["gui"] = gui_mock
sys.modules["gui.settingsDialogs"] = gui_mock.settingsDialogs

textInfos_mock = types.ModuleType("textInfos")
textInfos_mock.POSITION_CARET = 1
textInfos_mock.UNIT_CHARACTER = 2
sys.modules["textInfos"] = textInfos_mock

# Import Auto Braille modules
import autoBraille
from autoBraille import scripts_data, segmenter, translator


def test_1_sub_microsecond_ascii_fast_path():
	print("\n=== 1. Testing Sub-Microsecond Pure ASCII Fast Path ===")
	ascii_samples = [
		"Hello world!",
		"The quick brown fox jumps over the lazy dog 1234567890.",
		"Auto Braille delivers seamless multi-script translation for NVDA.",
		"printf(\"Score: %d\\n\", totalScore);",
	]
	for sample in ascii_samples:
		assert not scripts_data.has_non_ascii_latin(sample), f"ASCII false positive on: {sample}"

	non_ascii_samples = [
		("Kühlschrank", True),
		("Straße", True),
		("français", True),
		("cœur", True),
		("İstanbul", True),
		("Barış", True),
		("¿Cómo estás?", True),
		("café", True),
		("København", True),
	]
	for text, expected in non_ascii_samples:
		assert scripts_data.has_non_ascii_latin(text) == expected, f"Failed on: {text}"

	# Benchmark 100,000 iterations to verify < 0.5 microseconds per execution
	test_prose = "The quick brown fox jumps over the lazy dog and types code in Python."
	iterations = 100_000
	t0 = time.perf_counter()
	for _ in range(iterations):
		scripts_data.has_non_ascii_latin(test_prose)
	elapsed = time.perf_counter() - t0
	per_check_us = (elapsed / iterations) * 1_000_000
	print(f"ASCII fast-path check latency: {per_check_us:.4f} microseconds (Target: < 0.50 µs)")
	assert per_check_us < 0.50, f"ASCII check too slow: {per_check_us} µs"
	print("Sub-microsecond ASCII fast path verified successfully!")


def test_2_german_diacritics_and_atomic_locking():
	print("\n=== 2. Testing German Diacritics & Atomic Word Locking ===")
	active_latin = ["en-ueb-g1.ctb", "de-g1.ctb"]

	# Test individual word detection
	assert scripts_data.detect_latin_sub_language_for_word("Straße", active_latin) == "de-g1.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("Kühlschrank", active_latin) == "de-g1.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("Mädchen", active_latin) == "de-g1.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("refrigerator", active_latin) is None

	# Test full mixed sentence segmentation
	text = "The German word for refrigerator is Kühlschrank and street is Straße."
	segments = segmenter.segment_text(
		text,
		active_latin_tables=active_latin,
		primary_table="en-ueb-g1.ctb",
	)

	# Verify invariant: perfect reconstruction without gaps or overlaps
	reconstructed = "".join(s[0] for s in segments)
	assert reconstructed == text, f"Reconstruction failed: {reconstructed!r} != {text!r}"

	# Verify atomic word locking: Kühlschrank and Straße must NEVER be sliced into character pieces
	seg_dict = {s[0].strip(" ."): s[3] for s in segments}
	assert "Kühlschrank" in seg_dict, "Kühlschrank was sliced into pieces!"
	assert seg_dict["Kühlschrank"] == "latin:de-g1.ctb", f"Kühlschrank assigned wrong table: {seg_dict['Kühlschrank']}"
	assert "Straße" in seg_dict, "Straße was sliced into pieces!"
	assert seg_dict["Straße"] == "latin:de-g1.ctb", f"Straße assigned wrong table: {seg_dict['Straße']}"

	print("German atomic word locking verified successfully!")


def test_3_french_accents_and_ligatures():
	print("\n=== 3. Testing French Accents & Ligatures ===")
	active_latin = ["en-ueb-g1.ctb", "fr-bfu-comp8.ctb"]

	assert scripts_data.detect_latin_sub_language_for_word("cœur", active_latin) == "fr-bfu-comp8.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("français", active_latin) == "fr-bfu-comp8.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("élève", active_latin) == "fr-bfu-comp8.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("hôpital", active_latin) == "fr-bfu-comp8.ctb"

	text = "The French word for heart is cœur and student is élève."
	segments = segmenter.segment_text(
		text,
		active_latin_tables=active_latin,
		primary_table="en-ueb-g1.ctb",
	)
	assert "".join(s[0] for s in segments) == text

	coeur_seg = [s for s in segments if "cœur" in s[0]][0]
	assert coeur_seg[3] == "latin:fr-bfu-comp8.ctb"
	eleve_seg = [s for s in segments if "élève" in s[0]][0]
	assert eleve_seg[3] == "latin:fr-bfu-comp8.ctb"

	print("French accents and ligatures verified successfully!")


def test_4_turkish_dotless_i_case_folding_safety():
	print("\n=== 4. Testing Turkish Dotless 'i' Case-Folding Safety ===")
	active_latin = ["en-ueb-g1.ctb", "tr-g1.ctb"]

	# Dotted capital İ (U+0130)
	assert scripts_data.detect_latin_sub_language_for_word("İstanbul", active_latin) == "tr-g1.ctb"
	# Dotless lower ı (U+0131)
	assert scripts_data.detect_latin_sub_language_for_word("ılık", active_latin) == "tr-g1.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("Barış", active_latin) == "tr-g1.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("öğrenci", active_latin) == "tr-g1.ctb"

	text = "İstanbul ve Ankara çok güzel şehirlerdir."
	segments = segmenter.segment_text(
		text,
		active_latin_tables=active_latin,
		primary_table="en-ueb-g1.ctb",
	)
	assert "".join(s[0] for s in segments) == text

	# Verify Turkish words are routed to Turkish table without corrupting dotless ı
	ist_seg = [s for s in segments if "İstanbul" in s[0]][0]
	assert ist_seg[3] == "latin:tr-g1.ctb"
	sehir_seg = [s for s in segments if "şehirlerdir" in s[0]][0]
	assert sehir_seg[3] == "latin:tr-g1.ctb"

	print("Turkish dotless 'i' case-folding safety verified successfully!")


def test_5_spanish_and_scandinavian():
	print("\n=== 5. Testing Spanish and Scandinavian Routing ===")
	active_spanish = ["en-ueb-g1.ctb", "es-g1.ctb"]
	assert scripts_data.detect_latin_sub_language_for_word("señor", active_spanish) == "es-g1.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("¡Hola", active_spanish) == "es-g1.ctb"

	sp_text = "¿Cómo estás? Muy bien, señor."
	sp_segs = segmenter.segment_text(sp_text, active_latin_tables=active_spanish, primary_table="en-ueb-g1.ctb")
	assert "".join(s[0] for s in sp_segs) == sp_text
	for seg in sp_segs:
		if any(w in seg[0] for w in ("Cómo", "estás", "señor")):
			assert seg[3] == "latin:es-g1.ctb"

	active_scand = ["en-ueb-g1.ctb", "da-dk-g1.ctb"]
	assert scripts_data.detect_latin_sub_language_for_word("København", active_scand) == "da-dk-g1.ctb"

	scand_text = "Han bor i København."
	sc_segs = segmenter.segment_text(scand_text, active_latin_tables=active_scand, primary_table="en-ueb-g1.ctb")
	assert "".join(s[0] for s in sc_segs) == scand_text
	kbh_seg = [s for s in sc_segs if "København" in s[0]][0]
	assert kbh_seg[3] == "latin:da-dk-g1.ctb"

	print("Spanish and Scandinavian routing verified successfully!")


def test_6_english_loanword_anchoring():
	print("\n=== 6. Testing English Loanword Anchoring ===")
	active_latin = ["en-ueb-g1.ctb", "fr-bfu-comp8.ctb", "de-g1.ctb"]

	# In an English sentence, 'café' and 'résumé' must stay in English UEB
	eng_clause = "I met her at the café and gave her my résumé."
	assert scripts_data.detect_latin_sub_language_for_word("café", active_latin, clause_context=eng_clause) is None
	assert scripts_data.detect_latin_sub_language_for_word("résumé", active_latin, clause_context=eng_clause) is None

	eng_segs = segmenter.segment_text(eng_clause, active_latin_tables=active_latin, primary_table="en-ueb-g1.ctb")
	assert "".join(s[0] for s in eng_segs) == eng_clause
	# All segments must remain primary 'latin' (English UEB)
	assert all(s[3] == "latin" for s in eng_segs)

	# In a German sentence, 'Café' with German stop words should route to German
	ger_clause = "Wir treffen uns im Café."
	detected = scripts_data.detect_latin_sub_language_for_word("Café", active_latin, clause_context=ger_clause)
	assert detected == "de-g1.ctb", f"Expected German table for Café in German sentence, got: {detected}"

	print("English loanword anchoring verified successfully!")


def test_7_shared_diacritic_disambiguation():
	print("\n=== 7. Testing Shared Diacritic Disambiguation ===")
	# German and Turkish both share 'ü' and 'ö'
	active_tables = ["en-ueb-g1.ctb", "de-g1.ctb", "tr-g1.ctb"]

	# Exclusive markers take immediate precedence
	assert scripts_data.detect_latin_sub_language_for_word("Barış", active_tables) == "tr-g1.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("Straße", active_tables) == "de-g1.ctb"

	# Kühlschrank contains German characteristic n-gram 'sch'
	assert scripts_data.detect_latin_sub_language_for_word("Kühlschrank", active_tables) == "de-g1.ctb"

	# Clause context disambiguates shared words like 'Gül' / 'Müller'
	turk_clause = "Gül ve lale çok güzel çiçeklerdir."
	ger_clause = "Herr Müller wohnt in der Nähe von München."

	assert scripts_data.detect_latin_sub_language_for_word("güzel", active_tables, clause_context=turk_clause) == "tr-g1.ctb"
	assert scripts_data.detect_latin_sub_language_for_word("Müller", active_tables, clause_context=ger_clause) == "de-g1.ctb"

	print("Shared diacritic disambiguation verified successfully!")


def test_8_multi_script_translation_and_cursor_routing():
	print("\n=== 8. Testing Multi-Script Translation & Cursor Routing ===")
	active_tables = ["en-ueb-g1.ctb", "de-g1.ctb"]

	translated_calls: List[Tuple[List[str], str]] = []
	def tracking_louis_translate(tableList, inbuf, typeform=None, mode=0, cursorPos=None):
		translated_calls.append((tableList, inbuf))
		n = len(inbuf)
		cells = [ord(c) % 256 for c in inbuf]
		b2r = list(range(n))
		r2b = list(range(n))
		cur = cursorPos if cursorPos is not None and 0 <= cursorPos <= n else None
		return cells, b2r, r2b, cur

	inbuf = "The German word is Kühlschrank."
	cells, b2r, r2b, final_cur = translator.multi_script_translate(
		tracking_louis_translate,
		active_tables,
		inbuf,
		cursorPos=10,
	)

	# Verify calls: Kühlschrank translated with German table, English with English table
	tables_used = [os.path.basename(call[0][0]) for call in translated_calls]
	assert "en-ueb-g1.ctb" in tables_used
	assert "de-g1.ctb" in tables_used

	# Verify cursor routing arrays match length invariant
	assert len(b2r) == len(cells)
	assert len(r2b) == len(inbuf)
	assert final_cur == 10

	# Verify tactile marker: Dot 8 applied under first cell of secondary language (Kühlschrank)
	# Find where Kühlschrank starts
	k_idx = inbuf.index("Kühlschrank")
	cell_for_k = r2b[k_idx]
	assert (cells[cell_for_k] & translator.BRAILLE_DOT_8) == translator.BRAILLE_DOT_8, "Dot 8 marker missing on secondary language switch!"

	print("Multi-script translation, cursor routing, and tactile markers verified 100%!")


def run_all_tests():
	print("=" * 60)
	print("RUNNING LATIN SUB-LANGUAGE DIACRITIC TEST SUITE")
	print("=" * 60)

	test_1_sub_microsecond_ascii_fast_path()
	test_2_german_diacritics_and_atomic_locking()
	test_3_french_accents_and_ligatures()
	test_4_turkish_dotless_i_case_folding_safety()
	test_5_spanish_and_scandinavian()
	test_6_english_loanword_anchoring()
	test_7_shared_diacritic_disambiguation()
	test_8_multi_script_translation_and_cursor_routing()

	print("\n" + "=" * 60)
	print("  ALL 8 LATIN SUB-LANGUAGE TESTS PASSED 100%!")
	print("=" * 60)


if __name__ == "__main__":
	run_all_tests()
