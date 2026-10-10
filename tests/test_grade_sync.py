#!/usr/bin/env python3
# coding: utf-8
"""Tests for Grade Synchronization and User Table Respect in Auto Braille.

Verifies that changing braille tables in NVDA (between Grade 1 and Grade 2, or across
different regional languages) is fully respected by Auto Braille without being downgraded
to Grade 1 by document language tags, fast-check bypassing, or static defaults.
"""

from __future__ import annotations

import os
import sys
import types

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
addon_dir = os.path.join(repo_root, "addon", "globalPlugins")
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

import builtins
builtins._ = lambda s: s

class DummyConf(dict):
    spec = {}
    def __init__(self):
        super().__init__()
        self['autoBraille'] = {
            'enabled': True,
            'primaryTable': 'auto',
            'primaryInputTable': 'auto',
            'primaryLanguage': 'auto',
            'activeTables': 'fa-ir-g1.utb',
            'autoSyncInputTable': True,
            'honorDocumentLang': True,
            'tactileMarker': 'none',
            'grade2BoundaryGuard': True,
            'detectLatinSubLanguages': True,
            'detectMath': True,
            'mathTable': 'en-ueb-math.ctb',
            'statusCellLanguage': 'none',
            'customDictionary': '',
        }
        self['braille'] = {
            'translationTable': 'en-ueb-g2.ctb',
            'inputTable': 'en-ueb-g2.ctb',
        }

config_mock = types.ModuleType('config')
config_mock.conf = DummyConf()
config_mock.post_configProfileSwitch = types.SimpleNamespace(register=lambda f: None)
sys.modules['config'] = config_mock

braille_mock = types.ModuleType('braille')
braille_mock.TABLES_DIR = r'C:\fake\tables'
braille_tables_mock = types.ModuleType('brailleTables')
braille_tables_mock.TABLES_DIR = r'C:\fake\tables'
braille_tables_mock._tablesDirs = {'app': r'C:\fake\tables'}

class DummyTable:
    def __init__(self, fn, dn, out=True, inp=True):
        self.fileName = fn
        self.displayName = dn
        self.output = out
        self.input = inp

available_tables = [
    DummyTable('en-ueb-g2.ctb', 'English (Unified) Grade 2'),
    DummyTable('en-ueb-g1.ctb', 'English (Unified) Grade 1'),
    DummyTable('en-us-g2.ctb', 'English (US) Grade 2'),
    DummyTable('en-us-g1.ctb', 'English (US) Grade 1'),
    DummyTable('de-g2.ctb', 'German Grade 2'),
    DummyTable('de-g1.ctb', 'German Grade 1'),
    DummyTable('ar-ar-g2.ctb', 'Arabic Grade 2'),
    DummyTable('ar-ar-g1.utb', 'Arabic Grade 1'),
    DummyTable('fa-ir-g1.utb', 'Persian Grade 1'),
]
braille_tables_mock.listTables = lambda: available_tables
sys.modules['braille'] = braille_mock
sys.modules['brailleTables'] = braille_tables_mock

addonHandler_mock = types.ModuleType('addonHandler')
addonHandler_mock.initTranslation = lambda: None
addonHandler_mock._ = lambda s: s
sys.modules['addonHandler'] = addonHandler_mock

globalPluginHandler_mock = types.ModuleType('globalPluginHandler')
class DummyGlobalPlugin:
    def terminate(self): pass
globalPluginHandler_mock.GlobalPlugin = DummyGlobalPlugin
sys.modules['globalPluginHandler'] = globalPluginHandler_mock

louis_mock = types.ModuleType('louis')
louis_mock.compbrlAtCursor = 1
sys.modules['louis'] = louis_mock

used_translations = []
def mock_translate(tableList, inbuf, **kwargs):
    tables = [os.path.basename(t) for t in tableList]
    used_translations.append((tables, inbuf))
    return [1] * len(inbuf), list(range(len(inbuf))), list(range(len(inbuf))), 0

louisHelper_mock = types.ModuleType('louisHelper')
louisHelper_mock.translate = mock_translate
sys.modules['louisHelper'] = louisHelper_mock

logHandler_mock = types.ModuleType('logHandler')
logHandler_mock.log = types.SimpleNamespace(
    info=lambda *a, **k: None,
    warning=lambda *a, **k: None,
    debug=lambda *a, **k: None,
    error=lambda *a, **k: None,
)
sys.modules['logHandler'] = logHandler_mock

current_focus_lang = None
class DummyFocus:
    @property
    def language(self):
        return current_focus_lang

api_mock = types.ModuleType('api')
api_mock.getFocusObject = lambda: DummyFocus() if current_focus_lang is not None else None
sys.modules['api'] = api_mock

brailleInput_mock = types.ModuleType('brailleInput')
brailleInput_mock.handler = None
brailleInput_mock.BrailleInputHandler = types.SimpleNamespace(input=lambda *a, **k: None)
sys.modules['brailleInput'] = brailleInput_mock

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
gui_mock.settingsDialogs = types.SimpleNamespace(
    SettingsPanel=object,
    NVDASettingsDialog=types.SimpleNamespace(categoryClasses=[]),
)
sys.modules["gui"] = gui_mock
sys.modules["gui.settingsDialogs"] = gui_mock.settingsDialogs

globalVars_mock = types.ModuleType("globalVars")
globalVars_mock.appArgs = types.SimpleNamespace(secureMode=False)
sys.modules["globalVars"] = globalVars_mock

scriptHandler_mock = types.ModuleType("scriptHandler")
scriptHandler_mock.script = lambda **kwargs: (lambda f: f)
sys.modules["scriptHandler"] = scriptHandler_mock

ui_mock = types.ModuleType("ui")
ui_mock.message = lambda msg: None
sys.modules["ui"] = ui_mock

from autoBraille import GlobalPlugin, input_sync, translator, scripts_data

def test_grade_respect():
    print("=== 1. Testing Pure English Respect for Grade 2 Table ===")
    plugin = GlobalPlugin()
    used_translations.clear()
    config_mock.conf['braille']['translationTable'] = 'en-ueb-g2.ctb'
    config_mock.conf['autoBraille']['primaryTable'] = 'auto'

    plugin._hooked_translate(['en-ueb-g2.ctb', 'braille-patterns.cti'], 'Hello world')
    assert len(used_translations) == 1, f"Expected 1 call, got {len(used_translations)}"
    tables, text = used_translations[0]
    assert 'en-ueb-g2.ctb' in tables, f"Expected en-ueb-g2.ctb in {tables}"
    print("Grade 2 output table respected on fast check!")

    print("\n=== 2. Testing Switching to Grade 1 Table ===")
    used_translations.clear()
    config_mock.conf['braille']['translationTable'] = 'en-ueb-g1.ctb'
    plugin._hooked_translate(['en-ueb-g1.ctb', 'braille-patterns.cti'], 'Hello world')
    assert len(used_translations) == 1
    tables, text = used_translations[0]
    assert 'en-ueb-g1.ctb' in tables, f"Expected en-ueb-g1.ctb in {tables}"
    print("Grade 1 output table respected when user changes table in NVDA!")

    print("\n=== 3. Testing Grade 2 Protection Against Document Language Tag Downgrade ===")
    global current_focus_lang
    current_focus_lang = "en"
    config_mock.conf['braille']['translationTable'] = 'en-ueb-g2.ctb'
    used_translations.clear()

    plugin._hooked_translate(['en-ueb-g2.ctb', 'braille-patterns.cti'], 'Hello world')
    assert len(used_translations) == 1
    tables, text = used_translations[0]
    assert 'en-ueb-g2.ctb' in tables, f"Expected en-ueb-g2.ctb, got {tables} (Grade was downgraded!)"
    print("Document language tag 'en' did NOT downgrade Grade 2 to Grade 1!")

    print("\n=== 4. Testing Mixed English and Persian Text with Grade 2 Primary Table ===")
    used_translations.clear()
    current_focus_lang = None
    config_mock.conf['braille']['translationTable'] = 'en-ueb-g2.ctb'
    config_mock.conf['autoBraille']['activeTables'] = 'fa-ir-g1.utb'

    plugin._hooked_translate(['en-ueb-g2.ctb', 'braille-patterns.cti'], 'Hello سلام world')
    # Expected: 3 segments (Hello [en-g2], سلام [fa-g1], world [en-g2])
    assert len(used_translations) == 3, f"Expected 3 translations, got {len(used_translations)}"
    assert 'en-ueb-g2.ctb' in used_translations[0][0], f"First segment should be G2: {used_translations[0]}"
    assert 'fa-ir-g1.utb' in used_translations[1][0], f"Second segment should be Persian: {used_translations[1]}"
    assert 'en-ueb-g2.ctb' in used_translations[2][0], f"Third segment should be G2: {used_translations[2]}"
    print("Mixed text preserved Grade 2 for English segments alongside Persian segments!")

    print("\n=== 5. Testing German Grade 2 Primary Table Selection ===")
    used_translations.clear()
    config_mock.conf['braille']['translationTable'] = 'de-g2.ctb'
    plugin._hooked_translate(['de-g2.ctb', 'braille-patterns.cti'], 'Guten Tag')
    assert len(used_translations) == 1
    tables, text = used_translations[0]
    assert 'de-g2.ctb' in tables, f"Expected de-g2.ctb in {tables}"
    print("German Grade 2 table respected!")

    print("\n=== 6. Testing Arabic Grade 2 Primary Table Selection ===")
    used_translations.clear()
    config_mock.conf['braille']['translationTable'] = 'ar-ar-g2.ctb'
    plugin._hooked_translate(['ar-ar-g2.ctb', 'braille-patterns.cti'], 'مرحبا بك')
    assert len(used_translations) == 1
    tables, text = used_translations[0]
    assert 'ar-ar-g2.ctb' in tables, f"Expected ar-ar-g2.ctb in {tables}"
    print("Arabic Grade 2 table respected!")

    print("\n=== 7. Testing Perkins Input Table Grade Synchronization ===")
    config_mock.conf['autoBraille']['primaryInputTable'] = 'auto'
    config_mock.conf['braille']['inputTable'] = 'en-ueb-g2.ctb'
    resolved_inp = input_sync.resolve_input_table_for_lang(0x0409)  # en-US
    assert resolved_inp == 'en-ueb-g2.ctb', f"Expected en-ueb-g2.ctb, got {resolved_inp}"

    config_mock.conf['braille']['inputTable'] = 'de-g2.ctb'
    config_mock.conf['braille']['translationTable'] = 'de-g2.ctb'
    resolved_inp_de = input_sync.resolve_input_table_for_lang(0x0407)  # de-DE
    assert resolved_inp_de == 'de-g2.ctb', f"Expected de-g2.ctb, got {resolved_inp_de}"
    print("Perkins braille input table respects NVDA's selected grade!")

    print("\n=== 8. Testing Foreign Document Language Tag Promotion to Grade 2 ===")
    # When user operates with primary Grade 2 table, foreign document spans resolve to Grade 2 companion
    config_mock.conf['braille']['translationTable'] = 'en-ueb-g2.ctb'
    chain_es = translator.resolve_segment_table("Hola amigos", 0, 11, "latin", ["en-ueb-g2.ctb"], doc_lang_spans=[(0, 11, "es")])
    assert 'es-g2.ctb' in os.path.basename(chain_es[0]), f"Expected es-g2.ctb, got {chain_es[0]}"
    print("Foreign document language tag promoted to Grade 2 companion when primary table is Grade 2!")

    print("\n=======================================================")
    print("  ALL GRADE SYNCHRONIZATION TESTS PASSED 100%!        ")
    print("=======================================================\n")

if __name__ == '__main__':
    test_grade_respect()
