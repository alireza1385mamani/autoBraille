import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add add-on path to sys.path dynamically
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
addon_dir = os.path.join(repo_root, "addon", "globalPlugins")
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

import types
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
            "activeTables": "fa-ir-g1.utb, ru-litbrl.ctb",
            "autoSyncInputTable": True,
            "honorDocumentLang": True,
            "tactileMarker": "none",
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
class GlobalPlugin: pass
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

ui_mock = types.ModuleType("ui")
ui_messages = []
ui_mock.message = lambda msg: ui_messages.append(msg)
sys.modules["ui"] = ui_mock

api_mock = types.ModuleType("api")
api_mock.getFocusObject = lambda: None
api_mock.getReviewPosition = lambda: None
sys.modules["api"] = api_mock

braille_messages = []
brailleInput_mock = types.ModuleType("brailleInput")
brailleInput_mock.handler = types.SimpleNamespace(table=DummyTable("en-ueb-g1.ctb", "English"))
braille_mock.handler = types.SimpleNamespace(message=lambda msg: braille_messages.append(msg))
sys.modules["brailleInput"] = brailleInput_mock

class DummyControl:
    def __init__(self, *a, **k): pass
    def SetValue(self, *a, **k): pass
    def SetSelection(self, *a, **k): pass
    def GetSelection(self): return 0
    def GetValue(self): return True
    def Bind(self, *a, **k): pass
    def Clear(self): pass
    def Append(self, item): pass
    def Add(self, *a, **k): pass

wx_mock = types.ModuleType("wx")
wx_mock.Dialog = DummyControl
wx_mock.Sizer = DummyControl
wx_mock.BoxSizer = DummyControl
wx_mock.CheckBox = DummyControl
wx_mock.Choice = DummyControl
wx_mock.StaticLine = DummyControl
wx_mock.StaticText = DummyControl
wx_mock.ListBox = DummyControl
wx_mock.Button = DummyControl
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
wx_mock.EVT_LISTBOX_DCLICK = 1
wx_mock.EVT_CHAR_HOOK = 2
wx_mock.EVT_BUTTON = 3
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
class DummyFieldCommand:
    def __init__(self, cmd, field):
        self.command = cmd
        self.field = field
textInfos_mock.FieldCommand = DummyFieldCommand
sys.modules["textInfos"] = textInfos_mock

from autoBraille import scripts_data, translator, segmenter
import autoBraille

print("=== 1. Testing Document Language Tag Resolution & Compatibility ===")
# 1. BCP-47 Tag Resolution
tag_cases = [
    ("fa", "arabic_persian"),
    ("fa-IR", "arabic_persian"),
    ("ar", "arabic_persian"),
    ("ar-SA", "arabic_persian"),
    ("en", "latin"),
    ("en-US", "latin"),
    ("ru", "cyrillic"),
    ("ru-RU", "cyrillic"),
    ("he", "hebrew"),
    ("he-IL", "hebrew"),
    ("hi", "indic_devanagari"),
    ("hi-IN", "indic_devanagari"),
]
for tag, expected_script in tag_cases:
    s = scripts_data.resolve_doc_lang_to_script(tag)
    assert s is not None and s.id == expected_script, f"Failed for tag {tag}: expected {expected_script}, got {s.id if s else None}"
print("All document language tag mappings passed!")

# 2. Compatibility Validation
assert scripts_data.is_script_compatible("سلام دنیا", "arabic_persian") == True
assert scripts_data.is_script_compatible("Hello world", "arabic_persian") == False  # Inaccurate!
assert scripts_data.is_script_compatible("12345 ,.?!", "arabic_persian") == True   # Neutral
assert scripts_data.is_script_compatible("Hello world", "latin") == True
assert scripts_data.is_script_compatible("سلام دنیا", "latin") == False           # Inaccurate!
assert scripts_data.is_script_compatible("12345 ,.?!", "latin") == True            # Neutral
print("All script compatibility validations passed!")

print("\n=== 2. Testing Document Language Tag Segmentation (Feature 4) ===")
# Text with accurate doc tags
text = "Hello سلام world"
doc_spans = [(0, 6, "en"), (6, 11, "fa"), (11, 16, "en")]
segs = translator.segment_with_doc_langs(text, doc_spans, {"latin", "arabic_persian"}, "latin")
print("Segments with accurate doc tags:", segs)
assert len(segs) == 3
assert segs[0][3] == "latin"
assert segs[1][3] == "arabic_persian"
assert segs[2][3] == "latin"

# Text with INACCURATE doc tags (e.g. author tagged Persian text as English)
inaccurate_text = "سلام"
inaccurate_spans = [(0, 4, "en")] # Inaccurate tag!
segs2 = translator.segment_with_doc_langs(inaccurate_text, inaccurate_spans, {"latin", "arabic_persian"}, "latin")
print("Segments with inaccurate doc tag (fallback to Unicode detector):", segs2)
assert len(segs2) == 1
assert segs2[0][3] == "arabic_persian", f"Expected arabic_persian fallback, got {segs2[0][3]}"
print("Document language segmentation and fallback passed!")

print("\n=== 3. Testing Tactile Boundary Indicators (Feature 3) ===")
# Mock original_translate to return cell values based on character length
def mock_translate(table, inbuf, typeform=None, mode=0, cursorPos=None):
    cells = [1] * len(inbuf) # Each char gets cell value 1
    b2r = list(range(len(inbuf)))
    r2b = list(range(len(inbuf)))
    return cells, b2r, r2b, 0

# Test dot8_first: Dot 8 on first cell of secondary language switch
config_mock.conf["autoBraille"]["tactileMarker"] = "dot8_first"
config_mock.conf["autoBraille"]["primaryTable"] = "en-ueb-g1.ctb"
mixed_text = "Hi سلام"
cells, b2r, r2b, cur = translator.multi_script_translate(
    mock_translate, ["en-ueb-g1.ctb"], mixed_text
)
print("Cells with dot8_first marker:", cells)
# First segment is "Hi " (3 chars) -> cells 0, 1, 2
# Second segment is "سلام" (4 chars) -> cells 3, 4, 5, 6
# Cell 3 should have Dot 8 added: 1 | 0x80 = 129
assert cells[0] == 1, f"Expected cell 0 to be 1, got {cells[0]}"
assert cells[3] == 1 | 0x80, f"Expected cell 3 to have dot 8 (129), got {cells[3]}"
assert cells[4] == 1, f"Expected cell 4 to be unmodified (1), got {cells[4]}"

# Test dots78_secondary: Underline all secondary language cells with dots 7 and 8
config_mock.conf["autoBraille"]["tactileMarker"] = "dots78_secondary"
cells78, b2r78, r2b78, cur78 = translator.multi_script_translate(
    mock_translate, ["en-ueb-g1.ctb"], mixed_text
)
print("Cells with dots78_secondary marker:", cells78)
assert cells78[0] == 1
assert cells78[1] == 1
assert cells78[2] == 1
# All cells in second segment ("سلام") must have 0xC0 added: 1 | 0xC0 = 193
for c in cells78[3:]:
    assert c == 1 | 0xC0, f"Expected cell to have dots 7 and 8 (193), got {c}"

# Test dot7_first
config_mock.conf["autoBraille"]["tactileMarker"] = "dot7_first"
cells7, _, _, _ = translator.multi_script_translate(
    mock_translate, ["en-ueb-g1.ctb"], mixed_text
)
assert cells7[3] == 1 | 0x40, f"Expected cell 3 to have dot 7 (65), got {cells7[3]}"
print("Tactile boundary markers (dot8, dot7, dots78) verified successfully!")

print("\n=== 4. Testing Spoken & Braille Flashed Announcement (Feature 3) ===")
plugin = autoBraille.GlobalPlugin.__new__(autoBraille.GlobalPlugin)

# Mock caret on a Persian character
class MockTextInfo:
    def __init__(self, text, lang=None):
        self.text = text
        self.lang = lang
    def copy(self):
        return self
    def expand(self, unit):
        pass
    def getTextWithFields(self, formatConfig=None):
        if self.lang:
            return [DummyFieldCommand("formatChange", {"language": self.lang})]
        return []

class MockFocusObj:
    def __init__(self, text, lang=None):
        self._ti = MockTextInfo(text, lang)
    def makeTextInfo(self, pos):
        return self._ti

api_mock.getFocusObject = lambda: MockFocusObj("ک", "fa-IR")
plugin.script_announceLanguageAtCaret(None)
print("Spoken messages:", ui_messages)
print("Braille messages:", braille_messages)
assert len(ui_messages) == 1
assert "Persian" in ui_messages[0] or "fa-ir" in ui_messages[0]
assert len(braille_messages) == 1
print("Spoken and Braille flashed announcement verified successfully!")

print("\n=== 5. Testing Settings Panel makeSettings() ===")
class DummySizerHelper:
    def __init__(self, *a, **k): pass
    def addItem(self, item): return item
    def addLabeledControl(self, label, ctrlClass, choices=None):
        return ctrlClass()

class DummyControl:
    def __init__(self, *a, **k): pass
    def SetValue(self, *a, **k): pass
    def SetSelection(self, *a, **k): pass
    def GetSelection(self): return 0
    def GetValue(self): return True
    def Bind(self, *a, **k): pass
    def Clear(self): pass
    def Append(self, item): pass

wx_mock.CheckBox = DummyControl
wx_mock.Choice = DummyControl
wx_mock.StaticLine = DummyControl
wx_mock.StaticText = DummyControl
wx_mock.ListBox = DummyControl
wx_mock.Button = DummyControl
gui_mock.guiHelper.BoxSizerHelper = DummySizerHelper

panel = autoBraille.AutoBrailleSettingsPanel.__new__(autoBraille.AutoBrailleSettingsPanel)
panel.makeSettings(DummyControl())
print("AutoBrailleSettingsPanel.makeSettings() executed without UnboundLocalError!")

print("\nALL FEATURE 3 AND FEATURE 4 TESTS PASSED 100%!")

