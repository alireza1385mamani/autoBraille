# coding: utf-8
"""Auto Braille: Universal Multi-Script In-Line Braille Translation and Perkins Input for NVDA.

Automatically detects language scripts (Arabic/Persian, Cyrillic, Hebrew, Greek,
Indic/South Asian, East Asian CJK, Southeast Asian, African, Caucasian, and Latin)
within any text and dynamically translates each segment with its respective Liblouis
braille table across every braille display supported by NVDA.

Also provides bi-directional Perkins braille input auto-switching, keeping the braille
keyboard language in sync with the active Windows keyboard layout in real time.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional, Tuple

import addonHandler
import api
import braille
import brailleInput
import brailleTables
import config
import globalPluginHandler
import gui
from gui.settingsDialogs import SettingsPanel
from logHandler import log
import louisHelper
from scriptHandler import script
import ui
import wx

from . import input_sync
from .language_dialogs import AddTableDialog, EditTableDialog, AddLanguageDialog, EditLanguageDialog
from . import scripts_data
from . import segmenter
from . import translator

addonHandler.initTranslation()

# Build comprehensive confspec dynamically from scripts_data
confspec: Dict[str, str] = {
	# General & Primary
	"enabled": "boolean(default=True)",
	"primaryLanguage": "string(default=latin)",
	"primaryTable": "string(default=auto)",
	"autoSyncInputTable": "boolean(default=True)",
	"primaryInputTable": "string(default=auto)",
	"activeTables": "string(default=fa-ir-g1.utb)",
	"activeLanguages": "string(default=arabic_persian)",
	"tactileMarker": "string(default=none)",
	"honorDocumentLang": "boolean(default=True)",
	# Legacy keys for backward compatibility with existing configs
	"enableArabicPersian": "boolean(default=True)",
	"tableArabicPersian": "string(default=fa-ir-g1.utb)",
	"enableArabicPersianInput": "boolean(default=True)",
	"inputTableArabicPersian": "string(default=fa-ir-g1.utb)",
	"enableCyrillic": "boolean(default=True)",
	"tableCyrillic": "string(default=ru-litbrl.ctb)",
	"enableCyrillicInput": "boolean(default=True)",
	"inputTableCyrillic": "string(default=ru-litbrl.ctb)",
	"enableHebrew": "boolean(default=True)",
	"tableHebrew": "string(default=he-IL.utb)",
	"enableHebrewInput": "boolean(default=True)",
	"inputTableHebrew": "string(default=he-IL.utb)",
	"enableGreek": "boolean(default=True)",
	"tableGreek": "string(default=el.ctb)",
	"enableGreekInput": "boolean(default=True)",
	"inputTableGreek": "string(default=el.ctb)",
	"enableDevanagari": "boolean(default=True)",
	"tableDevanagari": "string(default=hi-in-g1.utb)",
	"enableDevanagariInput": "boolean(default=True)",
	"inputTableDevanagari": "string(default=hi-in-g1.utb)",
}

for s in scripts_data.SCRIPTS:
	if s.id != "latin":
		confspec[f"enable_{s.id}"] = f"boolean(default={s.default_enabled})"
		confspec[f"table_{s.id}"] = f"string(default={s.default_output_table})"
		confspec[f"enable_input_{s.id}"] = "boolean(default=True)"
		confspec[f"input_table_{s.id}"] = f"string(default={s.default_input_table})"

config.conf.spec["autoBraille"] = confspec


class AutoBrailleSettingsPanel(SettingsPanel):
	"""Streamlined Settings panel for Auto Braille with Active Languages List."""

	# Translators: Title of the Auto Braille settings panel
	title = _("Auto Braille")

	def makeSettings(self, settingsSizer: wx.Sizer) -> None:
		cfg = config.conf.get("autoBraille", {})
		self.available_output_tables = [t for t in brailleTables.listTables() if t.output]
		self.available_input_tables = [t for t in brailleTables.listTables() if t.input]

		# Table display name lookup cache
		self.tbl_names: Dict[str, str] = {
			t.fileName: t.displayName for t in brailleTables.listTables()
		}

		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		# =============================================================
		# 1. Master Switches & Primary / Latin Language
		# =============================================================
		self.enabledCheckbox = sHelper.addItem(
			wx.CheckBox(
				self,
				label=_("Enable &automatic multi-language braille output translation"),
			)
		)
		self.enabledCheckbox.SetValue(cfg.get("enabled", True))

		self.autoSyncInputCb = sHelper.addItem(
			wx.CheckBox(
				self,
				label=_("Automatically &sync Perkins braille input with active Windows keyboard layout"),
			)
		)
		self.autoSyncInputCb.SetValue(cfg.get("autoSyncInputTable", True))

		self.honorDocLangCb = sHelper.addItem(
			wx.CheckBox(
				self,
				label=_("Honor &document language tags in web and office documents (e.g. HTML, Word)"),
			)
		)
		self.honorDocLangCb.SetValue(cfg.get("honorDocumentLang", True))

		self.tactileMarkerOptions = [
			("none", _("None")),
			("dot8_first", _("Dot 8 under first cell of language change")),
			("dot7_first", _("Dot 7 under first cell of language change")),
			("dots78_secondary", _("Dots 7 and 8 underline under secondary language cells")),
		]
		self.tactileMarkerChoice = sHelper.addLabeledControl(
			_("&Tactile indicator for language boundaries:"),
			wx.Choice,
			choices=[opt[1] for opt in self.tactileMarkerOptions],
		)
		cur_marker = cfg.get("tactileMarker", "none")
		marker_idx = 0
		for idx, (m_id, opt_label) in enumerate(self.tactileMarkerOptions):
			if m_id == cur_marker:
				marker_idx = idx
				break
		self.tactileMarkerChoice.SetSelection(marker_idx)

		# Primary Output Table
		self.sorted_output_tables = sorted(self.available_output_tables, key=lambda t: t.displayName.lower())
		prim_out_choices = [_("Automatic (Use active NVDA output table)")] + [
			t.displayName for t in self.sorted_output_tables
		]
		self.primaryChoice = sHelper.addLabeledControl(
			_("&Primary output braille table:"), wx.Choice, choices=prim_out_choices
		)
		cur_primary = cfg.get("primaryTable", "auto")
		prim_out_idx = 0
		if cur_primary and cur_primary != "auto":
			for idx, t in enumerate(self.sorted_output_tables):
				if t.fileName == cur_primary:
					prim_out_idx = idx + 1
					break
		self.primaryChoice.SetSelection(prim_out_idx)

		# Primary Input Table
		self.sorted_input_tables = sorted(self.available_input_tables, key=lambda t: t.displayName.lower())
		prim_inp_choices = [_("Automatic (Follow active NVDA input table)")] + [
			t.displayName for t in self.sorted_input_tables
		]
		self.primaryInputChoice = sHelper.addLabeledControl(
			_("Primary Perkins &input braille table:"), wx.Choice, choices=prim_inp_choices
		)
		cur_inp = cfg.get("primaryInputTable", "auto")
		prim_inp_idx = 0
		if cur_inp and cur_inp != "auto":
			for idx, t in enumerate(self.sorted_input_tables):
				if t.fileName == cur_inp:
					prim_inp_idx = idx + 1
					break
		self.primaryInputChoice.SetSelection(prim_inp_idx)

		# =============================================================
		# 2. Active Secondary Braille Tables List
		# =============================================================
		sHelper.addItem(wx.StaticLine(self))
		sHelper.addItem(
			wx.StaticText(self, label=_("Active Secondary Braille Tables (Auto-Detected):"))
		)

		self.tablesList = wx.ListBox(self, style=wx.LB_SINGLE)
		sHelper.addItem(self.tablesList)
		self.tablesList.Bind(wx.EVT_LISTBOX_DCLICK, self.onConfigureTable)
		self.tablesList.Bind(wx.EVT_CHAR_HOOK, self.onListKey)

		# Load active tables from config
		self.active_items: List[Dict[str, str]] = []
		raw_tables = cfg.get("activeTables")
		if raw_tables:
			if isinstance(raw_tables, str):
				table_files = [t.strip() for t in raw_tables.split(",") if t.strip()]
			else:
				table_files = list(raw_tables)
		else:
			raw_active = cfg.get("activeLanguages")
			if raw_active:
				if isinstance(raw_active, str):
					s_ids = [p.strip() for p in raw_active.split(",") if p.strip()]
				else:
					s_ids = list(raw_active)
				table_files = []
				for s_id in s_ids:
					tbl = cfg.get(f"table_{s_id}")
					if not tbl:
						info = scripts_data.get_script_info(s_id)
						tbl = info.default_output_table if info else "fa-ir-g1.utb"
					table_files.append(tbl)
			else:
				table_files = ["fa-ir-g1.utb"]

		for tbl in table_files:
			s_info = scripts_data.resolve_table_to_script(tbl)
			inp_tbl = cfg.get(f"inputTable_{tbl}")
			if not inp_tbl or inp_tbl == "auto":
				inp_tbl = s_info.default_input_table if s_info else tbl
			self.active_items.append({
				"out_table": tbl,
				"inp_table": inp_tbl,
			})

		self.refreshTablesList()

		# =============================================================
		# 3. Action Buttons (Add, Configure, Remove)
		# =============================================================
		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.addButton = wx.Button(self, label=_("&Add Table..."))
		self.addButton.Bind(wx.EVT_BUTTON, self.onAddTable)
		btn_sizer.Add(self.addButton, 0, wx.RIGHT, 5)

		self.editButton = wx.Button(self, label=_("&Configure Table..."))
		self.editButton.Bind(wx.EVT_BUTTON, self.onConfigureTable)
		btn_sizer.Add(self.editButton, 0, wx.RIGHT, 5)

		self.removeButton = wx.Button(self, label=_("&Remove Table"))
		self.removeButton.Bind(wx.EVT_BUTTON, self.onRemoveTable)
		btn_sizer.Add(self.removeButton, 0)

		sHelper.addItem(btn_sizer)

	def formatItemDisplay(self, item: Dict[str, str]) -> str:
		out_dn = self.tbl_names.get(item["out_table"], item["out_table"])
		inp_dn = self.tbl_names.get(item["inp_table"], item["inp_table"])
		return f"{out_dn} ({item['out_table']})  —  Input: {inp_dn}"

	def refreshTablesList(self, select_idx: int = -1) -> None:
		self.tablesList.Clear()
		for item in self.active_items:
			self.tablesList.Append(self.formatItemDisplay(item))
		if self.active_items:
			if 0 <= select_idx < len(self.active_items):
				self.tablesList.SetSelection(select_idx)
			else:
				self.tablesList.SetSelection(0)

	def onListKey(self, event: wx.KeyEvent) -> None:
		key = event.GetKeyCode()
		if key == wx.WXK_DELETE:
			self.onRemoveTable(event)
		elif key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			self.onConfigureTable(event)
		else:
			event.Skip()

	def selectedPrimaryOutTable(self) -> str:
		p_sel = self.primaryChoice.GetSelection()
		if p_sel <= 0 or p_sel > len(self.sorted_output_tables):
			return "auto"
		return self.sorted_output_tables[p_sel - 1].fileName

	def selectedPrimaryInpTable(self) -> str:
		pinp_sel = self.primaryInputChoice.GetSelection()
		if pinp_sel <= 0 or pinp_sel > len(self.sorted_input_tables):
			return "auto"
		return self.sorted_input_tables[pinp_sel - 1].fileName

	def onAddTable(self, event: wx.Event) -> None:
		existing_files = [item["out_table"] for item in self.active_items]
		prim_file = self.selectedPrimaryOutTable()
		dlg = AddTableDialog(
			self,
			existing_files,
			self.available_output_tables,
			self.available_input_tables,
			primary_table_file=prim_file,
		)
		if dlg.ShowModal() == wx.ID_OK:
			out_tbl, inp_tbl = dlg.get_result()
			found = False
			for item in self.active_items:
				if item["out_table"] == out_tbl:
					item["inp_table"] = inp_tbl
					found = True
					break
			if not found:
				self.active_items.append({
					"out_table": out_tbl,
					"inp_table": inp_tbl,
				})
			self.refreshTablesList(select_idx=len(self.active_items) - 1)
		dlg.Destroy()

	def onConfigureTable(self, event: wx.Event) -> None:
		sel = self.tablesList.GetSelection()
		if sel == wx.NOT_FOUND or not (0 <= sel < len(self.active_items)):
			gui.messageBox(
				_("Please select a braille table from the list to configure."),
				_("Auto Braille"),
				wx.OK | wx.ICON_INFORMATION,
				self,
			)
			return

		item = self.active_items[sel]
		dlg = EditTableDialog(
			self,
			item["out_table"],
			item["inp_table"],
			available_output_tables=self.available_output_tables,
			available_input_tables=self.available_input_tables,
		)
		if dlg.ShowModal() == wx.ID_OK:
			out_tbl, inp_tbl = dlg.get_result()
			item["out_table"] = out_tbl
			item["inp_table"] = inp_tbl
			self.refreshTablesList(select_idx=sel)
		dlg.Destroy()

	def onRemoveTable(self, event: wx.Event) -> None:
		sel = self.tablesList.GetSelection()
		if sel == wx.NOT_FOUND or not (0 <= sel < len(self.active_items)):
			return
		self.active_items.pop(sel)
		new_sel = min(sel, len(self.active_items) - 1)
		self.refreshTablesList(select_idx=new_sel)

	def onSave(self) -> None:
		cfg = config.conf["autoBraille"]

		# Master switches & Primary tables
		cfg["enabled"] = self.enabledCheckbox.GetValue()
		cfg["autoSyncInputTable"] = self.autoSyncInputCb.GetValue()
		cfg["honorDocumentLang"] = self.honorDocLangCb.GetValue()
		marker_sel = self.tactileMarkerChoice.GetSelection()
		if 0 <= marker_sel < len(self.tactileMarkerOptions):
			cfg["tactileMarker"] = self.tactileMarkerOptions[marker_sel][0]

		prim_out = self.selectedPrimaryOutTable()
		prim_inp = self.selectedPrimaryInpTable()
		cfg["primaryTable"] = prim_out
		cfg["primaryInputTable"] = prim_inp

		prim_script = scripts_data.resolve_table_to_script(prim_out)
		cfg["primaryLanguage"] = prim_script.id

		# Save Active Tables list
		active_out_list = [item["out_table"] for item in self.active_items]
		cfg["activeTables"] = ",".join(active_out_list)

		# Save per-table input table and sync script keys
		active_script_ids = []
		for item in self.active_items:
			tbl = item["out_table"]
			inp_tbl = item["inp_table"]
			cfg[f"inputTable_{tbl}"] = inp_tbl

			s_info = scripts_data.resolve_table_to_script(tbl)
			if s_info:
				active_script_ids.append(s_info.id)
				cfg[f"enable_{s_info.id}"] = True
				cfg[f"table_{s_info.id}"] = tbl
				cfg[f"enable_input_{s_info.id}"] = True
				cfg[f"input_table_{s_info.id}"] = inp_tbl

				legacy_enable = translator.LEGACY_ENABLE_KEYS.get(s_info.id)
				if legacy_enable:
					cfg[legacy_enable] = True
				legacy_table = translator.LEGACY_TABLE_KEYS.get(s_info.id)
				if legacy_table:
					cfg[legacy_table] = tbl

		cfg["activeLanguages"] = ",".join(active_script_ids)

		# Invalidate internal translation, regex, and input caches
		input_sync.invalidate_cache()
		translator._table_path_cache.clear()
		translator._table_chain_cache.clear()
		segmenter.clear_regex_cache()

		# Refresh braille display output immediately
		if braille.handler and api.getFocusObject():
			braille.handler.handleGainFocus(api.getFocusObject())


_orig_braille_input: Optional[Callable[..., Any]] = None


def _hooked_braille_input(handler_self: Any, dots: int, *args: Any, **kwargs: Any) -> Any:
	"""Intercept Perkins dot entry and ensure input table matches active keyboard layout."""
	try:
		if config.conf.get("autoBraille", {}).get("autoSyncInputTable", True):
			input_sync.sync_input_table()
	except Exception:
		pass
	if _orig_braille_input:
		return _orig_braille_input(handler_self, dots, *args, **kwargs)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Global plugin hooking translation and Perkins input for universal multi-script braille."""

	scriptCategory = _("Auto Braille")

	def __init__(self) -> None:
		super().__init__()
		global _orig_braille_input

		# Hook output translation
		self._orig_translate = louisHelper.translate
		louisHelper.translate = self._hooked_translate

		# Hook Perkins braille keyboard input
		_orig_braille_input = getattr(brailleInput.BrailleInputHandler, "input", None)
		if _orig_braille_input:
			brailleInput.BrailleInputHandler.input = _hooked_braille_input

		try:
			from gui.settingsDialogs import NVDASettingsDialog

			NVDASettingsDialog.categoryClasses.append(AutoBrailleSettingsPanel)
		except Exception:
			log.warning("Auto Braille: could not register settings panel", exc_info=True)

		log.info("Auto Braille loaded successfully with streamlined active languages manager")

	def terminate(self) -> None:
		global _orig_braille_input

		louisHelper.translate = self._orig_translate
		if _orig_braille_input:
			brailleInput.BrailleInputHandler.input = _orig_braille_input
			_orig_braille_input = None
		try:
			from gui.settingsDialogs import NVDASettingsDialog

			NVDASettingsDialog.categoryClasses.remove(AutoBrailleSettingsPanel)
		except Exception:
			pass
		super().terminate()

	def event_gainFocus(self, obj: Any, nextHandler: Callable[..., Any]) -> None:
		"""Synchronize braille input table when active application or window changes."""
		nextHandler()
		try:
			# Zero overhead during NVDA startup: only sync if brailleInput handler is active
			if brailleInput.handler and config.conf.get("autoBraille", {}).get("autoSyncInputTable", True):
				input_sync.sync_input_table()
		except Exception:
			pass

	def _hooked_translate(
		self,
		tableList: List[str],
		inbuf: str,
		typeform: Optional[List[int]] = None,
		mode: int = 0,
		cursorPos: Optional[int] = None,
	) -> Tuple[List[int], List[int], List[int], Optional[int]]:
		"""Wrapper around louisHelper.translate intercepting multi-script text."""
		if not config.conf.get("autoBraille", {}).get("enabled", True) or not inbuf:
			return self._orig_translate(tableList, inbuf, typeform=typeform, mode=mode, cursorPos=cursorPos)

		primary_script = translator.get_primary_script(tableList)
		enabled_scripts = translator.get_enabled_scripts(tableList)
		secondary_scripts = {s for s in enabled_scripts if s != primary_script}

		doc_spans: Optional[List[Tuple[int, int, str]]] = None
		if config.conf.get("autoBraille", {}).get("honorDocumentLang", True):
			try:
				obj = api.getFocusObject()
				if obj:
					doc_lang = getattr(obj, "language", None)
					if not doc_lang and hasattr(obj, "makeTextInfo"):
						try:
							from textInfos import POSITION_CARET
							ti = obj.makeTextInfo(POSITION_CARET)
							if ti:
								fields = ti.getTextWithFields(formatConfig={"fontAttributeReporting": 0})
								for cmd in fields:
									if hasattr(cmd, "command") and cmd.command == "formatChange" and hasattr(cmd, "field"):
										doc_lang = cmd.field.get("language")
										if doc_lang:
											break
						except Exception:
							pass
					if doc_lang:
						doc_spans = [(0, len(inbuf), doc_lang)]
			except Exception:
				pass

		tactile_marker = config.conf.get("autoBraille", {}).get("tactileMarker", "none")

		# Fast check: If text contains no characters belonging to any enabled secondary script, no doc spans, and no tactile markers
		if not doc_spans and tactile_marker == "none" and not segmenter.has_secondary_scripts(inbuf, secondary_scripts):
			primary_tbl = config.conf.get("autoBraille", {}).get("primaryTable", "auto")
			if primary_tbl and primary_tbl != "auto":
				chain = translator.get_table_chain_for_file(primary_tbl)
				return self._orig_translate(chain, inbuf, typeform=typeform, mode=mode, cursorPos=cursorPos)
			elif primary_script != "latin":
				chain = translator.get_script_table_chain(primary_script, tableList)
				return self._orig_translate(chain, inbuf, typeform=typeform, mode=mode, cursorPos=cursorPos)
			return self._orig_translate(tableList, inbuf, typeform=typeform, mode=mode, cursorPos=cursorPos)

		# Mixed or secondary script detected, doc spans present, or tactile markers active
		return translator.multi_script_translate(
			self._orig_translate,
			tableList,
			inbuf,
			typeform=typeform,
			mode=mode,
			cursorPos=cursorPos,
			doc_lang_spans=doc_spans,
		)

	@script(
		description=_("Toggles automatic universal multi-script braille translation on and off"),
		category=_("Auto Braille"),
	)
	def script_toggleAutoBraille(self, gesture: Any) -> None:
		new_val = not config.conf.get("autoBraille", {}).get("enabled", True)
		config.conf["autoBraille"]["enabled"] = new_val
		msg = _("Auto Braille enabled") if new_val else _("Auto Braille disabled")
		ui.message(msg)
		if braille.handler and api.getFocusObject():
			braille.handler.handleGainFocus(api.getFocusObject())

	@script(
		description=_("Cycles or toggles Perkins braille keyboard input language"),
		category=_("Auto Braille"),
	)
	def script_toggleBrailleInputLanguage(self, gesture: Any) -> None:
		input_sync.toggle_input_language()

	@script(
		description=_("Announces the language and braille table at the caret or review cursor"),
		category=_("Auto Braille"),
	)
	def script_announceLanguageAtCaret(self, gesture: Any) -> None:
		obj = api.getFocusObject()
		char = ""
		doc_lang = None

		# 1. Try to get character and formatting at caret
		if obj:
			try:
				from textInfos import POSITION_CARET, UNIT_CHARACTER
				info = obj.makeTextInfo(POSITION_CARET)
				char_info = info.copy()
				char_info.expand(UNIT_CHARACTER)
				char = char_info.text
				# Check for document language format field
				try:
					fields = char_info.getTextWithFields(formatConfig={"fontAttributeReporting": 0})
					for cmd in fields:
						if hasattr(cmd, "command") and cmd.command == "formatChange" and hasattr(cmd, "field"):
							doc_lang = cmd.field.get("language")
							if doc_lang:
								break
				except Exception:
					pass
			except Exception:
				pass

		# 2. Try review position if caret didn't yield text
		if not char:
			try:
				from textInfos import UNIT_CHARACTER
				rev_info = api.getReviewPosition()
				if rev_info:
					c_info = rev_info.copy()
					c_info.expand(UNIT_CHARACTER)
					char = c_info.text
			except Exception:
				pass

		# 3. Resolve script and table
		s_info = None
		if doc_lang and config.conf.get("autoBraille", {}).get("honorDocumentLang", True):
			resolved = scripts_data.resolve_doc_lang_to_script(doc_lang)
			if resolved and (not char or scripts_data.is_script_compatible(char, resolved.id)):
				s_info = resolved

		if not s_info:
			if char:
				s_info = scripts_data.get_script_for_char(char)
			else:
				s_info = scripts_data.get_script_info(translator.get_primary_script())

		if not s_info:
			s_info = scripts_data.get_script_info("latin")

		script_name = s_info.name if s_info else "Latin"
		table_chain = translator.get_script_table_chain(s_info.id if s_info else "latin", [])
		table_file = os.path.basename(table_chain[0]) if table_chain else "en-ueb-g1.ctb"

		table_disp = table_file
		try:
			for t in brailleTables.listTables():
				if t.fileName == table_file:
					table_disp = t.displayName
					break
		except Exception:
			pass

		if char and not char.isspace():
			msg = _("{char}: {lang} ({table})").format(char=char, lang=script_name, table=table_disp)
		else:
			msg = _("{lang} ({table})").format(lang=script_name, table=table_disp)

		ui.message(msg)
		if braille.handler:
			try:
				braille.handler.message(msg)
			except Exception:
				pass

