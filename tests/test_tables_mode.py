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

# Mock NVDA modules before importing autoBraille
import types
import builtins
builtins._ = lambda s: s

class DummyConf(dict):
    spec = {}
    def __init__(self):
        super().__init__()
        self["autoBraille"] = {
            "enabled": True,
            "primaryTable": "auto",
            "primaryInputTable": "auto",
            "activeTables": "fa-ir-g1.utb, ru-litbrl.ctb",
            "autoSyncInputTable": True,
        }
        self["braille"] = {
            "translationTable": "en-ueb-g1.ctb",
            "inputTable": "en-ueb-g1.ctb",
        }

if "config" in sys.modules:
    config_mock = sys.modules["config"]
    config_mock.conf = DummyConf()
else:
    config_mock = types.ModuleType("config")
    config_mock.conf = DummyConf()
    sys.modules["config"] = config_mock

braille_mock = types.ModuleType("braille")
braille_mock.TABLES_DIR = r"C:\fake\tables"
braille_mock.handler = None
class DummyTable:
    def __init__(self, fn, dn, o=True, i=True):
        self.fileName = fn
        self.displayName = dn
        self.output = o
        self.input = i
braille_tables_mock = types.ModuleType("brailleTables")
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
ui_mock.message = lambda msg: print(f"UI MSG: {msg}")
sys.modules["ui"] = ui_mock

api_mock = types.ModuleType("api")
api_mock.getFocusObject = lambda: None
sys.modules["api"] = api_mock

brailleInput_mock = types.ModuleType("brailleInput")
brailleInput_mock.handler = types.SimpleNamespace(table=DummyTable("en-ueb-g1.ctb", "English"))
sys.modules["brailleInput"] = brailleInput_mock

wx_mock = types.ModuleType("wx")
wx_mock.Dialog = object
wx_mock.Sizer = object
wx_mock.BoxSizer = object
wx_mock.VERTICAL = 1
wx_mock.HORIZONTAL = 2
wx_mock.ALL = 1
wx_mock.EXPAND = 2
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

# Now test the modules
from autoBraille import scripts_data, translator, input_sync

print("--- Testing scripts_data.resolve_table_to_script ---")
cases = [
    ("fa-ir-g1.utb", "arabic_persian"),
    ("ar-ar-g1.utb", "arabic_persian"),
    ("ru-litbrl.ctb", "cyrillic"),
    ("he-IL.utb", "hebrew"),
    ("el.ctb", "greek"),
    ("hi-in-g1.utb", "indic_devanagari"),
    ("zh-tw.ctb", "cjk_chinese"),
    ("ja-kantenji.utb", "cjk_japanese"),
    ("ko-2006.ctb", "cjk_korean"),
    ("en-ueb-g1.ctb", "latin"),
    ("de-g1.ctb", "latin"),
    ("fr-bfu-comp6.utb", "latin"),
    ("unknown-table.utb", "latin"),
]
for tbl, expected in cases:
    res = scripts_data.resolve_table_to_script(tbl)
    assert res.id == expected, f"Failed for {tbl}: expected {expected}, got {res.id if res else None}"
print("All table-to-script resolutions passed!")

print("--- Testing translator ---")
sec_tables = translator.get_active_secondary_tables()
print("Active secondary tables:", sec_tables)
assert sec_tables == ["fa-ir-g1.utb", "ru-litbrl.ctb"], f"Unexpected sec_tables: {sec_tables}"

primary_script = translator.get_primary_script()
print("Primary script:", primary_script)
assert primary_script == "latin", f"Expected latin, got {primary_script}"

enabled_scripts = translator.get_enabled_scripts()
print("Enabled scripts:", enabled_scripts)
assert "arabic_persian" in enabled_scripts
assert "cyrillic" in enabled_scripts
assert "latin" in enabled_scripts

# Test input_sync
print("--- Testing input_sync.resolve_input_table_for_lang ---")
# Persian layout (0x0429) -> primary lang is 0x29
persian_tbl = input_sync.resolve_input_table_for_lang(0x0429)
print("Persian layout input table:", persian_tbl)
assert persian_tbl == "fa-ir-g1.utb", f"Expected fa-ir-g1.utb, got {persian_tbl}"

# Russian layout (0x0419) -> primary lang is 0x19
russian_tbl = input_sync.resolve_input_table_for_lang(0x0419)
print("Russian layout input table:", russian_tbl)
assert russian_tbl == "ru-litbrl.ctb", f"Expected ru-litbrl.ctb, got {russian_tbl}"

# English layout (0x0409) -> primary lang is 0x09
english_tbl = input_sync.resolve_input_table_for_lang(0x0409)
print("English layout input table:", english_tbl)
assert english_tbl == "en-ueb-g1.ctb", f"Expected en-ueb-g1.ctb, got {english_tbl}"

print("\n--- Testing Multiple Active Primary Tables in translator ---")
# Test 1: Default 'auto'
config_mock.conf["autoBraille"]["activePrimaryTables"] = "auto"
p_tables = translator.get_active_primary_tables()
print("Default active primary tables:", p_tables)
assert p_tables == ["en-ueb-g1.ctb"], f"Expected ['en-ueb-g1.ctb'], got {p_tables}"

# Test 2: Comma-separated multiple primary tables
config_mock.conf["autoBraille"]["activePrimaryTables"] = "en-ueb-g1.ctb, es-g1.ctb"
p_tables = translator.get_active_primary_tables()
print("Configured active primary tables:", p_tables)
assert p_tables == ["en-ueb-g1.ctb", "es-g1.ctb"], f"Expected ['en-ueb-g1.ctb', 'es-g1.ctb'], got {p_tables}"

# Test 3: Multiple primary tables in candidate tables
candidates_latin = translator.get_candidate_tables_for_script("latin")
print("Latin candidate tables:", candidates_latin)
assert "en-ueb-g1.ctb" in candidates_latin
assert "es-g1.ctb" in candidates_latin

# Test 4: get_active_latin_tables includes all active primary tables
latin_active = translator.get_active_latin_tables()
print("Active Latin tables:", latin_active)
assert latin_active[0] == "en-ueb-g1.ctb"
assert latin_active[1] == "es-g1.ctb"

# Test 5: input_sync with multiple primary tables
# Spanish layout (0x040A)
config_mock.conf["autoBraille"]["inputTable_es-g1.ctb"] = "es-g1.ctb"
spanish_inp = input_sync.resolve_input_table_for_lang(0x040A)
print("Spanish layout input table:", spanish_inp)
assert spanish_inp == "es-g1.ctb", f"Expected es-g1.ctb, got {spanish_inp}"

print("\n--- Testing AutoBrailleSettingsPanel Primary Tables UI Logic ---")
class DummyControl:
    def __init__(self, *a, **k):
        self._val = True
        self._sel = 0
        self._items = []
    def GetValue(self): return self._val
    def SetValue(self, v): self._val = v
    def GetSelection(self): return self._sel
    def SetSelection(self, s): self._sel = s
    def Append(self, item): self._items.append(item)
    def Clear(self): self._items.clear()
    def Bind(self, *a, **k): pass

class DummySizerHelper:
    def __init__(self, *a, **k): pass
    def addItem(self, item): return item
    def addLabeledControl(self, label, ctrlClass, choices=None):
        return ctrlClass(choices=choices)

wx_mock.ListBox = DummyControl
wx_mock.Button = DummyControl
wx_mock.Choice = DummyControl
wx_mock.CheckBox = DummyControl
wx_mock.StaticLine = DummyControl
wx_mock.StaticText = DummyControl
wx_mock.NOT_FOUND = -1
wx_mock.ICON_INFORMATION = 64
wx_mock.EVT_BUTTON = 1
wx_mock.EVT_CHOICE = 2
wx_mock.EVT_LISTBOX = 3
wx_mock.EVT_LISTBOX_DCLICK = 4
wx_mock.EVT_CHAR_HOOK = 5
gui_mock.guiHelper = types.SimpleNamespace(BoxSizerHelper=DummySizerHelper)
gui_mock.settingsDialogs.SettingsPanel = DummyControl

import autoBraille
from autoBraille import language_dialogs

panel = autoBraille.AutoBrailleSettingsPanel.__new__(autoBraille.AutoBrailleSettingsPanel)
panel.available_output_tables = braille_tables_mock.listTables()
panel.available_input_tables = braille_tables_mock.listTables()
panel.sorted_output_tables = sorted(panel.available_output_tables, key=lambda t: t.displayName.lower())
panel.sorted_input_tables = sorted(panel.available_input_tables, key=lambda t: t.displayName.lower())
panel.tbl_names = {t.fileName: t.displayName for t in panel.available_output_tables}
panel.primaryTablesList = DummyControl()
panel.tablesList = DummyControl()
panel.math_tables = panel.sorted_output_tables
panel.mathTableChoice = DummyControl()
panel.enabledCheckbox = DummyControl()
panel.autoSyncInputCb = DummyControl()
panel.honorDocLangCb = DummyControl()
panel.grade2GuardCb = DummyControl()
panel.detectLatinSubLanguagesCb = DummyControl()
panel.detectMathCb = DummyControl()
panel.tactileMarkerOptions = [("none", "None")]
panel.tactileMarkerChoice = DummyControl()
panel.statusCellOptions = [("none", "None")]
panel.statusCellChoice = DummyControl()
panel.custom_dictionary_entries = []
panel.active_items = []

# Initial state: 'auto'
panel.primary_active_items = [{"out_table": "auto", "inp_table": "auto"}]
panel.refreshPrimaryTablesList()
assert len(panel.primaryTablesList._items) == 1
assert "Automatic" in panel.primaryTablesList._items[0]
print("Primary tables list initialized with Automatic correctly!")

# Add a primary table (should replace 'auto' since it was the sole item)
class MockAddOk:
    def __init__(self, *a, **k): pass
    def ShowModal(self): return wx_mock.ID_OK
    def get_result(self): return ("en-ueb-g1.ctb", "en-ueb-g1.ctb")
    def Destroy(self): pass

orig_add_dlg = autoBraille.AddTableDialog
autoBraille.AddTableDialog = MockAddOk
language_dialogs.AddTableDialog = MockAddOk
panel.onAddPrimaryTable(None)
assert len(panel.primary_active_items) == 1
assert panel.primary_active_items[0]["out_table"] == "en-ueb-g1.ctb"
print("Adding first primary table replaced Automatic successfully!")

# Add a second primary table (should append)
class MockAddSecond:
    def __init__(self, *a, **k): pass
    def ShowModal(self): return wx_mock.ID_OK
    def get_result(self): return ("he-IL.utb", "he-IL.utb")
    def Destroy(self): pass

autoBraille.AddTableDialog = MockAddSecond
language_dialogs.AddTableDialog = MockAddSecond
panel.onAddPrimaryTable(None)
assert len(panel.primary_active_items) == 2
assert panel.primary_active_items[1]["out_table"] == "he-IL.utb"
print("Adding second primary table appended successfully!")

# Configure primary table
class MockEditOk:
    def __init__(self, *a, **k): pass
    def ShowModal(self): return wx_mock.ID_OK
    def get_result(self): return ("he-IL.utb", "en-ueb-g1.ctb")
    def Destroy(self): pass

orig_edit_dlg = autoBraille.EditTableDialog
autoBraille.EditTableDialog = MockEditOk
language_dialogs.EditTableDialog = MockEditOk
panel.primaryTablesList.SetSelection(1)
panel.onConfigurePrimaryTable(None)
assert panel.primary_active_items[1]["inp_table"] == "en-ueb-g1.ctb"
print("Configuring primary table updated input table mapping successfully!")

# Remove one primary table
panel.primaryTablesList.SetSelection(1)
panel.onRemovePrimaryTable(None)
assert len(panel.primary_active_items) == 1
assert panel.primary_active_items[0]["out_table"] == "en-ueb-g1.ctb"
print("Removing primary table succeeded!")

# Remove last primary table -> resets to 'auto'
panel.primaryTablesList.SetSelection(0)
panel.onRemovePrimaryTable(None)
assert len(panel.primary_active_items) == 1
assert panel.primary_active_items[0]["out_table"] == "auto"
print("Removing last primary table reset to Automatic successfully!")

# Reset button explicitly
panel.primary_active_items = [{"out_table": "ru-litbrl.ctb", "inp_table": "ru-litbrl.ctb"}]
panel.onResetPrimaryTable(None)
assert panel.primary_active_items[0]["out_table"] == "auto"
print("Reset to Automatic button verified!")

# Test onSave persistence
panel.primary_active_items = [
    {"out_table": "en-ueb-g1.ctb", "inp_table": "en-ueb-g1.ctb"},
    {"out_table": "ru-litbrl.ctb", "inp_table": "ru-litbrl.ctb"},
]
panel.onSave()
saved_cfg = config_mock.conf["autoBraille"]
assert saved_cfg["activePrimaryTables"] == "en-ueb-g1.ctb,ru-litbrl.ctb"
assert saved_cfg["primaryTable"] == "en-ueb-g1.ctb"
assert saved_cfg["primaryInputTable"] == "en-ueb-g1.ctb"
assert saved_cfg["inputTable_en-ueb-g1.ctb"] == "en-ueb-g1.ctb"
assert saved_cfg["inputTable_ru-litbrl.ctb"] == "ru-litbrl.ctb"
print("onSave persisted activePrimaryTables and per-table configurations successfully!")

# Restore dialogs
autoBraille.AddTableDialog = orig_add_dlg
language_dialogs.AddTableDialog = orig_add_dlg
autoBraille.EditTableDialog = orig_edit_dlg
language_dialogs.EditTableDialog = orig_edit_dlg

print("\nALL TABLE RESOLUTION, SYNC, AND PRIMARY TABLES UI TESTS PASSED SUCCESSFULLY!")
