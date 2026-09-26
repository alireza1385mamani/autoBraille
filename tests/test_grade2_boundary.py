# coding: utf-8
"""Comprehensive verification test suite for Contracted Braille (Grade 2) & Boundary Guarding."""

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
            "activeTables": "fa-ir-g1.utb, en-ueb-g2.ctb",
            "autoSyncInputTable": True,
            "honorDocumentLang": True,
            "grade2BoundaryGuard": True,
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
    DummyTable("en-ueb-g2.ctb", "English (Unified) Grade 2"),
    DummyTable("en-ueb-g1.ctb", "English (Unified) Grade 1"),
    DummyTable("fa-ir-g1.utb", "Persian Grade 1"),
    DummyTable("ar-ar-g2.ctb", "Arabic Grade 2"),
    DummyTable("ar-ar-g1.utb", "Arabic Grade 1"),
    DummyTable("de-g2.ctb", "German Grade 2"),
    DummyTable("de-g1.ctb", "German Grade 1"),
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

from autoBraille import scripts_data, translator, input_sync

print("=== 1. Testing Grade 2 Contracted Table Identification & Companion Lookup ===")
# Contracted check
assert scripts_data.is_contracted_table("en-ueb-g2.ctb") is True
assert scripts_data.is_contracted_table("ar-ar-g2.ctb") is True
assert scripts_data.is_contracted_table("de-g2.ctb") is True
assert scripts_data.is_contracted_table("en-ueb-g1.ctb") is False
assert scripts_data.is_contracted_table("fa-ir-g1.utb") is False

# Companion lookup
assert scripts_data.get_grade1_companion_table("en-ueb-g2.ctb") == "en-ueb-g1.ctb"
assert scripts_data.get_grade1_companion_table("ar-ar-g2.ctb") == "ar-ar-g1.utb"
assert scripts_data.get_grade1_companion_table("de-g2.ctb") == "de-g1.ctb"
assert scripts_data.get_grade1_companion_table("es-g2.ctb") == "es-g1.ctb"
assert scripts_data.get_grade1_companion_table("fr-bfu-g2.ctb") == "fr-bfu-comp8.ctb"
assert scripts_data.get_grade1_companion_table("ru-g2.ctb") == "ru-litbrl.ctb"
print("Grade 2 identification and companion lookups verified 100%!")

print("\n=== 2. Testing Single-Letter Word-Sign Candidate Detection ===")
# Isolated single letters (would mistakenly contract to whole words in Grade 2)
assert scripts_data.is_single_letter_wordsign_candidate("b") is True
assert scripts_data.is_single_letter_wordsign_candidate("c") is True
assert scripts_data.is_single_letter_wordsign_candidate("x") is True
assert scripts_data.is_single_letter_wordsign_candidate("(b)") is True
assert scripts_data.is_single_letter_wordsign_candidate("c.") is True
assert scripts_data.is_single_letter_wordsign_candidate(" p ") is True

# Standalone legitimate English words must NOT be flagged
assert scripts_data.is_single_letter_wordsign_candidate("a") is False
assert scripts_data.is_single_letter_wordsign_candidate("i") is False
assert scripts_data.is_single_letter_wordsign_candidate("A") is False
assert scripts_data.is_single_letter_wordsign_candidate("I") is False

# Multi-letter words must NOT be flagged
assert scripts_data.is_single_letter_wordsign_candidate("book") is False
assert scripts_data.is_single_letter_wordsign_candidate("can") is False
assert scripts_data.is_single_letter_wordsign_candidate("the") is False

# Numbers must NOT be flagged
assert scripts_data.is_single_letter_wordsign_candidate("1") is False
assert scripts_data.is_single_letter_wordsign_candidate("42") is False
print("Single-letter word-sign candidate detection verified 100%!")

print("\n=== 3. Testing Technical Identifier & Code Token Detection ===")
# Snake_case & symbols
assert scripts_data.is_technical_identifier("user_id") is True
assert scripts_data.is_technical_identifier("file_name") is True
assert scripts_data.is_technical_identifier("path/to/file") is True
assert scripts_data.is_technical_identifier(r"C:\docs\readme.txt") is True
assert scripts_data.is_technical_identifier("user@example.com") is True
assert scripts_data.is_technical_identifier("$variable") is True
assert scripts_data.is_technical_identifier("#include") is True

# CamelCase
assert scripts_data.is_technical_identifier("fileName") is True
assert scripts_data.is_technical_identifier("getData") is True
assert scripts_data.is_technical_identifier("recordCount") is True

# Natural literary English prose must NOT be flagged as code
assert scripts_data.is_technical_identifier("Hello world") is False
assert scripts_data.is_technical_identifier("This is a book") is False
assert scripts_data.is_technical_identifier("Knowledge is power") is False
print("Technical identifier and code detection verified 100%!")

print("\n=== 4. Testing Translation Engine Boundary Guarding ===")
active_tables = ["en-ueb-g2.ctb"]
full_text = "گزینه b را انتخاب کنید"

# 4.1. Single-letter variable 'b' in Persian text -> Falls back to Grade 1 companion en-ueb-g1.ctb!
chain_b = translator.resolve_segment_table("b", 6, 7, "latin", active_tables, full_inbuf=full_text)
assert "en-ueb-g1.ctb" in chain_b[0], f"Expected en-ueb-g1.ctb for single letter 'b', got {chain_b[0]}"

# 4.2. Full literary word 'book' in Persian text -> Uses Grade 2 en-ueb-g2.ctb!
full_text_book = "کتاب book را بخوانید"
chain_book = translator.resolve_segment_table("book", 5, 9, "latin", active_tables, full_inbuf=full_text_book)
assert "en-ueb-g2.ctb" in chain_book[0], f"Expected en-ueb-g2.ctb for full word 'book', got {chain_book[0]}"

# 4.3. Technical identifier 'user_id' -> Falls back to Grade 1 companion en-ueb-g1.ctb!
full_text_code = "متغیر user_id است"
chain_code = translator.resolve_segment_table("user_id", 6, 13, "latin", active_tables, full_inbuf=full_text_code)
assert "en-ueb-g1.ctb" in chain_code[0], f"Expected en-ueb-g1.ctb for identifier 'user_id', got {chain_code[0]}"

# 4.4. CamelCase identifier 'fileName' -> Falls back to Grade 1 companion en-ueb-g1.ctb!
full_text_camel = "تابع fileName اجرا شد"
chain_camel = translator.resolve_segment_table("fileName", 5, 13, "latin", active_tables, full_inbuf=full_text_camel)
assert "en-ueb-g1.ctb" in chain_camel[0], f"Expected en-ueb-g1.ctb for camelCase 'fileName', got {chain_camel[0]}"

# 4.5. Numeric boundary lookback: '123b' -> 'b' immediately follows '3' -> Grade 1 fallback!
full_text_num = "شماره 123b"
chain_num = translator.resolve_segment_table("b", 9, 10, "latin", active_tables, full_inbuf=full_text_num)
assert "en-ueb-g1.ctb" in chain_num[0], f"Expected en-ueb-g1.ctb for 'b' after digit, got {chain_num[0]}"

# 4.6. Boundary guarding disabled via config: 'b' stays on Grade 2 en-ueb-g2.ctb
config_mock.conf["autoBraille"]["grade2BoundaryGuard"] = False
chain_noguard = translator.resolve_segment_table("b", 6, 7, "latin", active_tables, full_inbuf=full_text)
assert "en-ueb-g2.ctb" in chain_noguard[0], f"Expected en-ueb-g2.ctb when guard is disabled, got {chain_noguard[0]}"
config_mock.conf["autoBraille"]["grade2BoundaryGuard"] = True

print("Translation engine Grade 2 boundary guarding verified 100%!")

print("\n=======================================================")
print("  ALL GRADE 2 BOUNDARY GUARDING TESTS PASSED 100%!    ")
print("=======================================================")
