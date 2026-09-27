# coding: utf-8
"""Comprehensive verification test suite for Auto Braille new features:
1. Math & STEM Auto-Detection (LaTeX, plain formulas, currency collision guards, punctuation detachment).
2. Hardware Status Cell Language Indicators (tactile language codes, display safety, modes).
3. App-Specific & Profile-Aware Braille Switching (config profile hooks, cache invalidation, display refresh).
4. Direct Braille Display Key Shortcuts / Chords (unassigned gestures in Auto Braille category).
5. Custom User Lexicon / Dictionary Overrides (word boundary locking, case sensitivity, dialogs).
"""

from __future__ import annotations

import builtins
import os
import sys
import types
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add add-on path to sys.path dynamically
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
addon_dir = os.path.join(repo_root, "addon", "globalPlugins")
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

builtins._ = lambda s: s

# Setup Mocks
config_mock = types.ModuleType("config")


class DummyConf(dict):
    spec = {}

    def __init__(self):
        super().__init__()
        self["autoBraille"] = {
            "enabled": True,
            "primaryTable": "en-ueb-g1.ctb",
            "primaryInputTable": "en-ueb-g1.ctb",
            "primaryLanguage": "latin",
            "activeTables": "fa-ir-g1.utb, de-g1.ctb",
            "autoSyncInputTable": True,
            "honorDocumentLang": True,
            "tactileMarker": "none",
            "grade2BoundaryGuard": True,
            "detectLatinSubLanguages": True,
            "detectMath": True,
            "mathTable": "en-ueb-math.ctb",
            "statusCellLanguage": "current",
            "customDictionary": "",
        }
        self["braille"] = {
            "translationTable": "en-ueb-g1.ctb",
            "inputTable": "en-ueb-g1.ctb",
        }


dummy_conf = DummyConf()
config_mock.conf = dummy_conf


class DummyExtensionPoint:
    def __init__(self):
        self.callbacks = []

    def register(self, cb):
        if cb not in self.callbacks:
            self.callbacks.append(cb)

    def unregister(self, cb):
        if cb in self.callbacks:
            self.callbacks.remove(cb)

    def notify(self, *args, **kwargs):
        for cb in self.callbacks:
            cb(*args, **kwargs)


config_mock.post_configProfileSwitch = DummyExtensionPoint()
sys.modules["config"] = config_mock

braille_mock = types.ModuleType("braille")
braille_mock.TABLES_DIR = r"C:\fake\tables"


class DummyDisplay:
    def __init__(self, num_status=2):
        self.numStatusCells = num_status
        self.displayed_cells = []
        self.displayed_status = []

    def display(self, cells, statusCells=None):
        self.displayed_cells = list(cells)
        self.displayed_status = list(statusCells) if statusCells is not None else []


class DummyBrailleHandler:
    def __init__(self, num_status=2):
        self.display = DummyDisplay(num_status=num_status)
        self.cells = [1, 2, 3]
        self.statusCells = [0] * num_status
        self.messages = []

    def message(self, msg):
        self.messages.append(msg)

    def handleGainFocus(self, obj):
        pass


braille_mock.handler = DummyBrailleHandler(num_status=2)
sys.modules["braille"] = braille_mock

braille_input_mock = types.ModuleType("brailleInput")


class DummyBrailleInputHandler:
    def __init__(self):
        self.inputTable = "en-ueb-g1.ctb"

    def input(self, dots, *args, **kwargs):
        pass


braille_input_mock.handler = DummyBrailleInputHandler()
braille_input_mock.BrailleInputHandler = DummyBrailleInputHandler
sys.modules["brailleInput"] = braille_input_mock

braille_tables_mock = types.ModuleType("brailleTables")
braille_tables_mock.TABLES_DIR = r"C:\fake\tables"
braille_tables_mock._tablesDirs = {"app": r"C:\fake\tables"}


class DummyTable:
    def __init__(self, fn, dn, o=True, i=True):
        self.fileName = fn
        self.displayName = dn
        self.output = o
        self.input = i


braille_tables_mock.listTables = lambda: [
    DummyTable("en-ueb-g1.ctb", "English (Unified) Grade 1"),
    DummyTable("en-ueb-g2.ctb", "English (Unified) Grade 2"),
    DummyTable("en-ueb-math.ctb", "Unified English Braille - Technical Math"),
    DummyTable("nemeth.ctb", "Nemeth Braille Code"),
    DummyTable("fa-ir-g1.utb", "Persian Grade 1"),
    DummyTable("de-g1.ctb", "German Grade 1"),
    DummyTable("fr-bfu-comp8.ctb", "French 8-dot Computer"),
    DummyTable("braille-patterns.cti", "Unicode Braille Patterns", False, False),
]
sys.modules["brailleTables"] = braille_tables_mock

addonHandler_mock = types.ModuleType("addonHandler")
addonHandler_mock.initTranslation = lambda: None
addonHandler_mock._ = lambda s: s
sys.modules["addonHandler"] = addonHandler_mock

globalVars_mock = types.ModuleType("globalVars")
globalVars_mock.appArgs = types.SimpleNamespace(secureMode=False)
sys.modules["globalVars"] = globalVars_mock

globalPluginHandler_mock = types.ModuleType("globalPluginHandler")


class DummyGlobalPlugin:
    def __init__(self):
        pass

    def terminate(self):
        pass


globalPluginHandler_mock.GlobalPlugin = DummyGlobalPlugin
globalPluginHandler_mock.runningPlugins = {}
sys.modules["globalPluginHandler"] = globalPluginHandler_mock

logHandler_mock = types.ModuleType("logHandler")
log_obj = types.SimpleNamespace(
    info=lambda *args, **kwargs: None,
    warning=lambda *args, **kwargs: None,
    error=lambda *args, **kwargs: None,
    debug=lambda *args, **kwargs: None,
)
logHandler_mock.log = log_obj
sys.modules["logHandler"] = logHandler_mock

ui_mock = types.ModuleType("ui")
ui_messages = []
ui_mock.message = lambda msg: ui_messages.append(msg)
sys.modules["ui"] = ui_mock

api_mock = types.ModuleType("api")
api_mock.getFocusObject = lambda: types.SimpleNamespace(language="en")
api_mock.getReviewPosition = lambda: None
sys.modules["api"] = api_mock

louis_mock = types.ModuleType("louis")
louis_mock.compbrlAtCursor = 1
sys.modules["louis"] = louis_mock

louisHelper_mock = types.ModuleType("louisHelper")


def dummy_translate(tableList, inbuf, typeform=None, mode=0, cursorPos=None):
    cells = [ord(c) % 255 for c in inbuf]
    b2r = list(range(len(inbuf)))
    r2b = list(range(len(inbuf)))
    return cells, b2r, r2b, cursorPos


louisHelper_mock.translate = dummy_translate
sys.modules["louisHelper"] = louisHelper_mock

scriptHandler_mock = types.ModuleType("scriptHandler")


def dummy_script(**kwargs):
    def decorator(func):
        for k, v in kwargs.items():
            setattr(func, k, v)
        return func

    return decorator


scriptHandler_mock.script = dummy_script
sys.modules["scriptHandler"] = scriptHandler_mock

gui_mock = types.ModuleType("gui")
guiHelper_mock = types.SimpleNamespace()


class DummyBoxSizerHelper:
    def __init__(self, parent, sizer=None):
        self.parent = parent
        self.sizer = sizer

    def addItem(self, item):
        return item

    def addLabeledControl(self, label, control_class, **kwargs):
        return control_class(self.parent, **kwargs)


guiHelper_mock.BoxSizerHelper = DummyBoxSizerHelper
gui_mock.guiHelper = guiHelper_mock
gui_mock.messageBox = lambda *args, **kwargs: None
sys.modules["gui"] = gui_mock

settingsDialogs_mock = types.ModuleType("gui.settingsDialogs")


class DummySettingsPanel:
    def __init__(self, parent):
        self.parent = parent


settingsDialogs_mock.SettingsPanel = DummySettingsPanel


class DummyNVDASettingsDialog:
    categoryClasses = []


settingsDialogs_mock.NVDASettingsDialog = DummyNVDASettingsDialog
sys.modules["gui.settingsDialogs"] = settingsDialogs_mock

# wx mock for testing settings panel & dialogs without wxPython runtime
wx_mock = types.ModuleType("wx")
wx_mock.ID_OK = 1
wx_mock.ID_CANCEL = 2
wx_mock.OK = 4
wx_mock.CANCEL = 8
wx_mock.VERTICAL = 1
wx_mock.HORIZONTAL = 2
wx_mock.ALL = 1
wx_mock.ALIGN_RIGHT = 2
wx_mock.RIGHT = 16
wx_mock.LEFT = 32
wx_mock.TOP = 64
wx_mock.BOTTOM = 128
wx_mock.LB_SINGLE = 1
wx_mock.NOT_FOUND = -1
wx_mock.WXK_DELETE = 127
wx_mock.WXK_RETURN = 13
wx_mock.WXK_NUMPAD_ENTER = 14
wx_mock.EVT_BUTTON = 1
wx_mock.EVT_CHOICE = 2
wx_mock.EVT_LISTBOX_DCLICK = 3
wx_mock.EVT_CHAR_HOOK = 4


class DummyWxWindow:
    def __init__(self, *args, **kwargs):
        self._val = kwargs.get("label", "")
        self.selection = 0

    def Bind(self, *args, **kwargs):
        pass

    def SetValue(self, v):
        self._val = v

    def GetValue(self):
        return self._val

    def SetSelection(self, idx):
        self.selection = idx

    def GetSelection(self):
        return self.selection

    def Clear(self):
        pass

    def Append(self, s):
        pass

    def SetSizerAndFit(self, sizer):
        pass

    def CenterOnParent(self):
        pass

    def CreateButtonSizer(self, flags):
        return DummyWxBoxSizer(wx_mock.HORIZONTAL)

    def Destroy(self):
        pass


class DummyWxBoxSizer:
    def __init__(self, orientation):
        pass

    def Add(self, *args, **kwargs):
        pass


wx_mock.Window = DummyWxWindow
wx_mock.Dialog = DummyWxWindow
wx_mock.CheckBox = DummyWxWindow
wx_mock.Choice = DummyWxWindow
wx_mock.TextCtrl = DummyWxWindow
wx_mock.ListBox = DummyWxWindow
wx_mock.Button = DummyWxWindow
wx_mock.StaticText = DummyWxWindow
wx_mock.StaticLine = DummyWxWindow
wx_mock.BoxSizer = DummyWxBoxSizer
sys.modules["wx"] = wx_mock

# Now import Auto Braille modules
import autoBraille
from autoBraille import scripts_data, segmenter, translator, language_dialogs


def test_math_stem_detection():
    print("\n=== 1. Testing Math & STEM Formula Detection ===")

    # 1.1 Fast path check
    assert scripts_data.has_math_candidate("Simple literary English text.") is False
    assert scripts_data.has_math_candidate("Solve $x^2 + 5 = 9$ now.") is True
    assert scripts_data.has_math_candidate("Consider f(x) = 2x + 1.") is True

    # 1.2 LaTeX Delimiters
    spans1 = scripts_data.find_math_spans(r"Let $x^2 = 4$ and $$y = \sqrt{x}$$ be true.")
    assert len(spans1) == 2
    assert spans1[0][2] == "$x^2 = 4$"
    assert spans1[1][2] == r"$$y = \sqrt{x}$$"

    spans2 = scripts_data.find_math_spans(r"Here is \(a + b = c\) and \[ \frac{1}{2} \]")
    assert len(spans2) == 2
    assert spans2[0][2] == r"\(a + b = c\)"
    assert spans2[1][2] == r"\[ \frac{1}{2} \]"

    # 1.3 Currency Collision Guard: Single dollar amounts are NOT math
    currency_text = "I bought a book for $50 and coffee for $4.99 at the shop."
    spans_curr = scripts_data.find_math_spans(currency_text)
    assert len(spans_curr) == 0, f"Currency mistakenly identified as math: {spans_curr}"

    # 1.4 Plain-text equation and trailing punctuation detachment
    plain_text = "Evaluate f(x) = 2x + 1, where x = 5."
    spans_plain = scripts_data.find_math_spans(plain_text)
    assert len(spans_plain) >= 1
    # Check that trailing comma is NOT inside the math formula
    math_expr = spans_plain[0][2]
    assert not math_expr.endswith(","), f"Math formula failed to detach trailing comma: {math_expr}"
    assert "f(x) = 2x + 1" in math_expr

    # 1.5 Full segmentation integration with math
    test_str = "The formula $f(x) = x^2$ is simple."
    segs = segmenter.segment_text(
        test_str,
        detect_math=True,
        math_table="en-ueb-math.ctb",
    )
    # Check seamless concatenation
    assert "".join(s[0] for s in segs) == test_str
    # Verify math tag
    math_segs = [s for s in segs if s[3].startswith("math:")]
    assert len(math_segs) == 1
    assert math_segs[0][0] == "$f(x) = x^2$"
    assert math_segs[0][3] == "math:en-ueb-math.ctb"

    # 1.6 Multilingual Math: Persian + LaTeX formula
    fa_math = "فرمول اینشتین $E = mc^2$ مشهور است."
    segs_fa = segmenter.segment_text(
        fa_math,
        primary_script="arabic_persian",
        detect_math=True,
        math_table="en-ueb-math.ctb",
    )
    assert "".join(s[0] for s in segs_fa) == fa_math
    assert segs_fa[0][3] == "arabic_persian"
    assert segs_fa[1][3] == "math:en-ueb-math.ctb"
    assert segs_fa[2][3] == "arabic_persian"

    # 1.7 Translator routing for math
    table_chain = translator.resolve_segment_table("$x^2$", 0, 5, "math:en-ueb-math.ctb", ["en-ueb-g1.ctb"])
    assert "en-ueb-math.ctb" in table_chain[0]

    print("Math & STEM formula detection and routing verified 100%!")


def test_hardware_status_cells():
    print("\n=== 2. Testing Hardware Status Cell Language Indicators ===")

    # 2.1 Dot definitions
    en_dots = scripts_data.get_status_cell_dots_for_lang("latin")
    assert en_dots == [0x11, 0x1D], f"Expected 'en' dots [0x11, 0x1D], got {en_dots}"

    fa_dots = scripts_data.get_status_cell_dots_for_lang("arabic_persian")
    assert fa_dots == [0x0B, 0x01], f"Expected 'fa' dots [0x0B, 0x01], got {fa_dots}"

    de_dots = scripts_data.get_status_cell_dots_for_lang("german")
    assert de_dots == [0x19, 0x11], f"Expected 'de' dots [0x19, 0x11], got {de_dots}"

    math_dots = scripts_data.get_status_cell_dots_for_lang("math:en-ueb-math.ctb")
    assert math_dots == [0x0D, 0x01], f"Expected 'ma' dots [0x0D, 0x01], got {math_dots}"

    # 2.2 GlobalPlugin apply_status_cells with 0 status cells (portable displays)
    braille_mock.handler.display = DummyDisplay(num_status=0)
    plugin = autoBraille.GlobalPlugin()
    plugin.apply_status_cells(update_display=True)
    # Should safely return without exception or crash

    # 2.3 GlobalPlugin apply_status_cells with 2 physical status cells
    braille_mock.handler.display = DummyDisplay(num_status=2)
    braille_mock.handler.statusCells = [0, 0]
    config_mock.conf["autoBraille"]["statusCellLanguage"] = "current"
    translator.last_active_language = "persian"

    plugin.apply_status_cells(update_display=True)
    assert braille_mock.handler.statusCells == [0x0B, 0x01]
    assert braille_mock.handler.display.displayed_status == [0x0B, 0x01]

    # Test switching to English in status cells
    translator.last_active_language = "latin"
    plugin.apply_status_cells(update_display=True)
    assert braille_mock.handler.statusCells == [0x11, 0x1D]

    # 2.4 Mode: "primary"
    config_mock.conf["autoBraille"]["statusCellLanguage"] = "primary"
    config_mock.conf["autoBraille"]["primaryLanguage"] = "latin"
    translator.last_active_language = "arabic_persian"
    plugin.apply_status_cells(update_display=True)
    # Even though last_active_language is Persian, primary mode shows English
    assert braille_mock.handler.statusCells == [0x11, 0x1D]

    plugin.terminate()
    print("Hardware status cell tactile indicators verified 100%!")


def test_profile_aware_switching():
    print("\n=== 3. Testing App-Specific & Profile-Aware Braille Switching ===")

    plugin = autoBraille.GlobalPlugin()
    assert plugin.onConfigProfileSwitch in config_mock.post_configProfileSwitch.callbacks

    # Verify that triggering profile switch clears caches and applies settings
    segmenter._scanner_cache["dummy"] = "cached"
    translator._table_chain_cache["dummy"] = ["cached"]

    config_mock.post_configProfileSwitch.notify()

    assert "dummy" not in segmenter._scanner_cache
    assert "dummy" not in translator._table_chain_cache

    plugin.terminate()
    assert plugin.onConfigProfileSwitch not in config_mock.post_configProfileSwitch.callbacks
    print("App-specific configuration profile switching verified 100%!")


def test_unassigned_display_shortcuts():
    print("\n=== 4. Testing Direct Braille Display Shortcuts / Chords ===")

    plugin = autoBraille.GlobalPlugin()

    # 4.1 Verify that scripts exist with category "Auto Braille"
    assert hasattr(plugin, "script_cycleSecondaryTable")
    assert getattr(plugin.script_cycleSecondaryTable, "category", "") == "Auto Braille"

    assert hasattr(plugin, "script_cyclePrimaryTable")
    assert getattr(plugin.script_cyclePrimaryTable, "category", "") == "Auto Braille"

    assert hasattr(plugin, "script_toggleMathDetection")
    assert getattr(plugin.script_toggleMathDetection, "category", "") == "Auto Braille"

    # 4.2 Verify no hardcoded gestures (__gestures__ is empty or not mapped)
    gestures = getattr(plugin, "__gestures__", {})
    assert "br(all):routing" not in gestures
    assert "kb:NVDA+control+shift+m" not in gestures

    # 4.3 Test cycling secondary tables
    config_mock.conf["autoBraille"]["activeTables"] = "fa-ir-g1.utb, de-g1.ctb"
    ui_messages.clear()
    plugin.script_cycleSecondaryTable(None)
    # The active table list should have rotated: de-g1.ctb is now first
    assert config_mock.conf["autoBraille"]["activeTables"].startswith("de-g1.ctb")
    assert any("Secondary braille table:" in m for m in ui_messages)

    # 4.4 Test toggling math detection
    config_mock.conf["autoBraille"]["detectMath"] = True
    plugin.script_toggleMathDetection(None)
    assert config_mock.conf["autoBraille"]["detectMath"] is False
    plugin.script_toggleMathDetection(None)
    assert config_mock.conf["autoBraille"]["detectMath"] is True

    # 4.5 Test cycling primary tables
    config_mock.conf["autoBraille"]["primaryTable"] = "en-ueb-g1.ctb"
    config_mock.conf["autoBraille"]["activeTables"] = "fa-ir-g1.utb, de-g1.ctb"
    plugin.script_cyclePrimaryTable(None)
    assert config_mock.conf["autoBraille"]["primaryTable"] == "fa-ir-g1.utb"

    plugin.terminate()
    print("Unassigned display gestures and cycling scripts verified 100%!")


def test_custom_dictionary_overrides():
    print("\n=== 5. Testing Custom User Lexicon / Dictionary Overrides ===")

    # 5.1 Serialization and Parsing
    entries = [
        {"pattern": "AutoBraille", "table": "en-ueb-g2.ctb", "case_sensitive": True},
        {"pattern": "NVDA", "table": "en-ueb-g1.ctb", "case_sensitive": False},
    ]
    serialized = scripts_data.serialize_custom_dictionary(entries)
    parsed = scripts_data.parse_custom_dictionary(serialized)
    assert len(parsed) == 2
    assert parsed[0]["pattern"] == "AutoBraille"
    assert parsed[1]["table"] == "en-ueb-g1.ctb"

    # 5.2 Word-boundary safety (No substring matching)
    # Entry for "in" should NOT match inside "morning" or "terminal"
    rule_in = [{"pattern": "in", "table": "fa-ir-g1.utb", "case_sensitive": False}]
    test_text = "Good morning in the terminal."
    segs = segmenter.segment_text(
        test_text,
        primary_script="latin",
        custom_dictionary=rule_in,
    )
    # Exactly one custom segment for the standalone preposition "in"
    custom_segs = [s for s in segs if s[3].startswith("custom:")]
    assert len(custom_segs) == 1
    assert custom_segs[0][0] == "in"
    assert custom_segs[0][1] == 13
    assert custom_segs[0][2] == 15
    assert "".join(s[0] for s in segs) == test_text

    # 5.3 Case sensitivity enforcement
    rule_cs = [
        {"pattern": "LaTeX", "table": "en-ueb-math.ctb", "case_sensitive": True},
    ]
    segs_cs1 = segmenter.segment_text("Reading LaTeX code.", custom_dictionary=rule_cs)
    assert any(s[3] == "custom:en-ueb-math.ctb" for s in segs_cs1)

    segs_cs2 = segmenter.segment_text("latex is lowercase.", custom_dictionary=rule_cs)
    assert not any(s[3] == "custom:en-ueb-math.ctb" for s in segs_cs2)

    # 5.4 Priority over math & literary
    rule_math_override = [
        {"pattern": "f(x) = x^2", "table": "en-ueb-g2.ctb", "case_sensitive": False},
    ]
    segs_prio = segmenter.segment_text(
        "Let f(x) = x^2 be true.",
        detect_math=True,
        custom_dictionary=rule_math_override,
    )
    # The custom rule overrides math detection
    assert any(s[3] == "custom:en-ueb-g2.ctb" for s in segs_prio)

    # 5.5 Dialogs instantiation and functionality
    edit_dlg = language_dialogs.EditCustomEntryDialog(
        wx_mock.Window(),
        pattern="Python",
        table="en-ueb-g2.ctb",
        case_sensitive=True,
        available_output_tables=braille_tables_mock.listTables(),
    )
    p, t, cs = edit_dlg.get_result()
    assert p == "Python"
    assert t == "en-ueb-g2.ctb"
    assert cs is True

    dict_dlg = language_dialogs.CustomDictionaryDialog(
        wx_mock.Window(),
        entries,
        available_output_tables=braille_tables_mock.listTables(),
    )
    assert len(dict_dlg.get_entries()) == 2

    print("Custom user dictionary overrides and dialogs verified 100%!")


if __name__ == "__main__":
    test_math_stem_detection()
    test_hardware_status_cells()
    test_profile_aware_switching()
    test_unassigned_display_shortcuts()
    test_custom_dictionary_overrides()

    print("\n" + "=" * 60)
    print("  ALL NEW FEATURES TESTS PASSED 100%!")
    print("=" * 60)
