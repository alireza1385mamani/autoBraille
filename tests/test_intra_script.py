# coding: utf-8
"""Comprehensive verification test suite for Intra-Script Multi-Language Disambiguation in Auto Braille."""

import sys
import os
import types

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add add-on path to sys.path dynamically
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
            "primaryTable": "fa-ir-g1.utb",
            "primaryInputTable": "fa-ir-g1.utb",
            "activeTables": "fa-ir-g1.utb, ar-ar-g1.utb, en-ueb-g1.ctb",
            "autoSyncInputTable": True,
            "honorDocumentLang": True,
            "tactileMarker": "none",
        }
        self["braille"] = {
            "translationTable": "fa-ir-g1.utb",
            "inputTable": "fa-ir-g1.utb",
        }
config_mock.conf = DummyConf()
sys.modules["config"] = config_mock

braille_mock = types.ModuleType("braille")
braille_mock.TABLES_DIR = r"C:\fake\tables"
class DummyTable:
    def __init__(self, fn, dn, o=True, i=True):
        self.fileName = fn
        self.displayName = dn
        self.output = o
        self.input = i
braille_tables_mock = types.ModuleType("brailleTables")
braille_tables_mock.TABLES_DIR = r"C:\fake\tables"
braille_tables_mock._tablesDirs = {"app": r"C:\fake\tables"}
braille_tables_mock.listTables = lambda: [
    DummyTable("en-ueb-g1.ctb", "English (Unified) Grade 1"),
    DummyTable("fa-ir-g1.utb", "Persian Grade 1"),
    DummyTable("ar-ar-g1.utb", "Arabic Grade 1"),
    DummyTable("fr-bfu-comp8.ctb", "French Computer 8-dot"),
    DummyTable("de-g1.ctb", "German Grade 1"),
    DummyTable("ru-litbrl.ctb", "Russian Literary"),
    DummyTable("he-IL.utb", "Hebrew"),
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

louis_mock = types.ModuleType("louis")
louis_mock.translate = lambda *a, **k: ([1, 2, 3], [0, 1, 2], [0, 1, 2], 0)
sys.modules["louis"] = louis_mock

louisHelper_mock = types.ModuleType("louisHelper")
louisHelper_mock.translate = lambda *a, **k: ([1, 2, 3], [0, 1, 2], [0, 1, 2], 0)
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

ui_messages = []
ui_mock = types.ModuleType("ui")
ui_mock.message = lambda msg: ui_messages.append(msg)
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
brailleInput_mock.handler = types.SimpleNamespace(table=DummyTable("fa-ir-g1.utb", "Persian"))
braille_messages = []
braille_mock.handler = types.SimpleNamespace(message=lambda msg: braille_messages.append(msg))
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

import autoBraille
from autoBraille import scripts_data, translator, input_sync

print("=== 1. Testing Specific Language Name Extraction ===")
assert scripts_data.get_language_name_for_table("fa-ir-g1.utb") == "Persian"
assert scripts_data.get_language_name_for_table("ar-ar-g1.utb") == "Arabic"
assert scripts_data.get_language_name_for_table("en-ueb-g1.ctb") == "English (Unified)"
assert scripts_data.get_language_name_for_table("fr-bfu-comp8.ctb") == "French"
assert scripts_data.get_language_name_for_table("de-g1.ctb") == "German"
assert scripts_data.get_language_name_for_table("ru-litbrl.ctb") == "Russian"
assert scripts_data.get_language_name_for_table("es-g1.ctb") == "Spanish"
assert scripts_data.get_language_name_for_table("uk.utb") == "Ukrainian"
print("All specific language names extracted accurately!")

print("\n=== 2. Testing Dynamic Secondary Table Defaults for Non-Latin Primary Users ===")
# Persian primary user -> English secondary
sec_fa = translator.get_default_secondary_table("fa-ir-g1.utb")
assert sec_fa == "en-ueb-g1.ctb", f"Expected en-ueb-g1.ctb for Persian primary, got {sec_fa}"

# Russian primary user -> English secondary
sec_ru = translator.get_default_secondary_table("ru-litbrl.ctb")
assert sec_ru == "en-ueb-g1.ctb", f"Expected en-ueb-g1.ctb for Russian primary, got {sec_ru}"

# Arabic primary user -> English secondary
sec_ar = translator.get_default_secondary_table("ar-ar-g1.utb")
assert sec_ar == "en-ueb-g1.ctb", f"Expected en-ueb-g1.ctb for Arabic primary, got {sec_ar}"

# English primary user -> Persian secondary
sec_en = translator.get_default_secondary_table("en-ueb-g1.ctb")
assert sec_en == "fa-ir-g1.utb", f"Expected fa-ir-g1.utb for English primary, got {sec_en}"
print("Dynamic secondary table defaults verified successfully!")

print("\n=== 3. Testing Loanword Stability (Zero-Flapping Heuristic) ===")
# Persian loanwords with Arabic-exclusive characters (ة, etc.)
loanword_fa1 = "دایرة‌المعارف"
loanword_fa2 = "نهایة"
loanword_fa3 = "خاصةً و عامةً"
candidates_arabic_persian = ["fa-ir-g1.utb", "ar-ar-g1.utb"]

res1 = scripts_data.detect_intra_script_table(loanword_fa1, candidates_arabic_persian)
assert res1 == "fa-ir-g1.utb", f"Expected fa-ir-g1.utb for {loanword_fa1}, got {res1}"

res2 = scripts_data.detect_intra_script_table(loanword_fa2, candidates_arabic_persian)
assert res2 == "fa-ir-g1.utb", f"Expected fa-ir-g1.utb for {loanword_fa2}, got {res2}"

res3 = scripts_data.detect_intra_script_table(loanword_fa3, candidates_arabic_persian)
assert res3 == "fa-ir-g1.utb", f"Expected fa-ir-g1.utb for {loanword_fa3}, got {res3}"

# Full Persian sentence with loanword
persian_sentence = "این یک دایرة‌المعارف بزرگ و معتبر است"
res_fa_sent = scripts_data.detect_intra_script_table(persian_sentence, candidates_arabic_persian)
assert res_fa_sent == "fa-ir-g1.utb", f"Expected fa-ir-g1.utb for Persian sentence, got {res_fa_sent}"

# English loanwords with European accents
candidates_latin = ["en-ueb-g1.ctb", "fr-bfu-comp8.ctb"]
loanword_en1 = "café"
loanword_en2 = "résumé"
loanword_en3 = "I drank a coffee at the café"

res_en1 = scripts_data.detect_intra_script_table(loanword_en1, candidates_latin)
assert res_en1 == "en-ueb-g1.ctb", f"Expected en-ueb-g1.ctb for {loanword_en1}, got {res_en1}"

res_en2 = scripts_data.detect_intra_script_table(loanword_en2, candidates_latin)
assert res_en2 == "en-ueb-g1.ctb", f"Expected en-ueb-g1.ctb for {loanword_en2}, got {res_en2}"

res_en3 = scripts_data.detect_intra_script_table(loanword_en3, candidates_latin)
assert res_en3 == "en-ueb-g1.ctb", f"Expected en-ueb-g1.ctb for English sentence, got {res_en3}"
print("Loanword stability (zero flapping on دایرة‌المعارف and café) verified 100%!")

print("\n=== 4. Testing Multi-Word Grammatical Stop-Word Disambiguation ===")
# Pure Arabic phrase with multiple Arabic grammatical particles (في, من, على, قال)
arabic_phrase = "قال المعلم: في التأني السلامة وفي العجلة الندامة"
res_ar = scripts_data.detect_intra_script_table(arabic_phrase, candidates_arabic_persian)
assert res_ar == "ar-ar-g1.utb", f"Expected ar-ar-g1.utb for Arabic phrase, got {res_ar}"

# Pure French phrase with multiple French grammatical particles (la, dans, nous, sommes)
french_phrase = "C'est la vie mon ami nous sommes dans la ville"
res_fr = scripts_data.detect_intra_script_table(french_phrase, candidates_latin)
assert res_fr == "fr-bfu-comp8.ctb", f"Expected fr-bfu-comp8.ctb for French phrase, got {res_fr}"
print("Multi-word grammatical phrase disambiguation verified 100%!")

print("\n=== 5. Testing Intra-Script Document Language Markup Switching ===")
# Document markup overrides intra-script candidate
spans = [(0, 10, "fa"), (10, 20, "ar")]
text_sample = "کتاب اول     قال المعلم"
table_chain_fa = translator.resolve_segment_table("کتاب اول", 0, 8, "arabic_persian", ["fa-ir-g1.utb", "ar-ar-g1.utb"], spans)
assert "fa-ir-g1.utb" in table_chain_fa[0], f"Expected fa-ir-g1.utb for fa span, got {table_chain_fa}"

table_chain_ar = translator.resolve_segment_table("قال المعلم", 12, 20, "arabic_persian", ["fa-ir-g1.utb", "ar-ar-g1.utb"], spans)
assert "ar-ar-g1.utb" in table_chain_ar[0], f"Expected ar-ar-g1.utb for ar span, got {table_chain_ar}"

# French document tag in Latin document
spans_lat = [(0, 5, "en"), (5, 15, "fr")]
table_chain_fr = translator.resolve_segment_table("bonjour", 6, 13, "latin", ["en-ueb-g1.ctb", "fr-bfu-comp8.ctb"], spans_lat)
assert "fr-bfu-comp8.ctb" in table_chain_fr[0], f"Expected fr-bfu-comp8.ctb for fr span, got {table_chain_fr}"
print("Document language markup intra-script switching verified 100%!")

print("\n=== 6. Testing Perkins Input Keyboard Synchronization ===")
# Persian keyboard (0x0429) -> fa-ir-g1.utb
inp_fa = input_sync.resolve_input_table_for_lang(0x0429)
assert inp_fa == "fa-ir-g1.utb", f"Expected fa-ir-g1.utb for LANGID 0x0429, got {inp_fa}"

# Arabic keyboard (0x0401 Saudi, 0x0801 Iraq) -> ar-ar-g1.utb
inp_ar = input_sync.resolve_input_table_for_lang(0x0401)
assert inp_ar == "ar-ar-g1.utb", f"Expected ar-ar-g1.utb for LANGID 0x0401, got {inp_ar}"
inp_ar_iq = input_sync.resolve_input_table_for_lang(0x0801)
assert inp_ar_iq == "ar-ar-g1.utb", f"Expected ar-ar-g1.utb for LANGID 0x0801, got {inp_ar_iq}"

# English keyboard (0x0409) -> en-ueb-g1.ctb
inp_en = input_sync.resolve_input_table_for_lang(0x0409)
assert inp_en == "en-ueb-g1.ctb", f"Expected en-ueb-g1.ctb for LANGID 0x0409, got {inp_en}"
print("Perkins input keyboard synchronization verified 100%!")

print("\n=== 7. Testing Caret Announcement with Specific Language Names ===")
plugin = autoBraille.GlobalPlugin.__new__(autoBraille.GlobalPlugin)

class MockTI:
    def __init__(self, text, lang=None):
        self.text = text
        self.lang = lang
    def copy(self): return self
    def expand(self, unit): pass
    def getTextWithFields(self, formatConfig=None):
        if self.lang:
            class Cmd:
                command = "formatChange"
                field = {"language": self.lang}
            return [Cmd()]
        return []

class MockObj:
    def __init__(self, text, lang=None):
        self._ti = MockTI(text, lang)
    def makeTextInfo(self, pos): return self._ti

# Announce Persian character
api_mock.getFocusObject = lambda: MockObj("گ", "fa")
ui_messages.clear()
braille_messages.clear()
plugin.script_announceLanguageAtCaret(None)
print("Persian announcement:", ui_messages[-1])
assert "Persian" in ui_messages[-1]
assert "Arabic / Persian" not in ui_messages[-1] # Ensure old generic category string is gone!

# Announce Arabic character in Arabic span
api_mock.getFocusObject = lambda: MockObj("ض", "ar")
ui_messages.clear()
braille_messages.clear()
plugin.script_announceLanguageAtCaret(None)
print("Arabic announcement:", ui_messages[-1])
assert "Arabic" in ui_messages[-1]
assert "Arabic / Persian" not in ui_messages[-1]

# Announce English character
api_mock.getFocusObject = lambda: MockObj("b", "en")
ui_messages.clear()
braille_messages.clear()
plugin.script_announceLanguageAtCaret(None)
print("English announcement:", ui_messages[-1])
assert "English" in ui_messages[-1]
assert "Primary / Latin" not in ui_messages[-1]

print("Caret announcements report specific language names verified 100%!")

print("\n=======================================================")
print("  ALL INTRA-SCRIPT MULTI-LANGUAGE TESTS PASSED 100%!   ")
print("=======================================================")
