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

print("\nALL TABLE RESOLUTION AND SYNC TESTS PASSED SUCCESSFULLY!")
