# coding: utf-8
"""Add and Edit Language modal dialogs for Auto Braille.

Provides accessible, clean modal dialogs to add any world writing system
and configure Liblouis output and Perkins input braille tables.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import brailleTables
import gui
import wx

try:
	_ = _  # type: ignore
except NameError:
	try:
		from addonHandler import initTranslation
		initTranslation()
	except Exception:
		_ = lambda s: s

try:
	from . import scripts_data
except ImportError:
	import scripts_data


def _filter_tables(
	available: List[Any],
	prefixes: Tuple[str, ...],
	keywords: Tuple[str, ...],
	show_all: bool = False,
) -> List[Any]:
	"""Filter Liblouis tables by script prefixes/keywords, or return all if show_all is True."""
	if show_all:
		return list(available)

	filtered = [
		t
		for t in available
		if any(t.fileName.lower().startswith(p.lower()) for p in prefixes)
		or any(k.lower() in t.displayName.lower() for k in keywords)
	]
	return filtered if filtered else list(available)


def _find_matching_input_table(out_table_file: str, available_input: List[Any]) -> int:
	"""Find the best matching input table index for a given output table."""
	for idx, t in enumerate(available_input):
		if t.fileName == out_table_file:
			return idx

	s_info = scripts_data.resolve_table_to_script(out_table_file)
	if s_info:
		target_inp = s_info.default_input_table
		for idx, t in enumerate(available_input):
			if t.fileName == target_inp:
				return idx
		for idx, t in enumerate(available_input):
			if any(t.fileName.lower().startswith(p.lower()) for p in s_info.table_prefixes):
				return idx

	return 0


class AddTableDialog(wx.Dialog):
	"""Modal dialog to select an output braille table and assign Perkins input table."""

	def __init__(
		self,
		parent: wx.Window,
		existing_table_files: List[str],
		available_output_tables: List[Any],
		available_input_tables: List[Any],
		primary_table_file: str = "auto",
	) -> None:
		# Translators: Title of the Add Table dialog
		super().__init__(parent, title=_("Add Secondary Braille Table"))

		self.output_tables = sorted(available_output_tables, key=lambda t: t.displayName.lower())
		self.input_tables = sorted(available_input_tables, key=lambda t: t.displayName.lower())
		self.existing_table_files = existing_table_files

		main_sizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=main_sizer)

		out_choices = [t.displayName for t in self.output_tables]
		# Translators: Label for the output braille table choice in Add Secondary Braille Table dialog.
		self.outputChoice = sHelper.addLabeledControl(
			_("&Output braille table:"), wx.Choice, choices=out_choices
		)

		initial_idx = 0
		for idx, t in enumerate(self.output_tables):
			if t.fileName not in existing_table_files and t.fileName != primary_table_file:
				initial_idx = idx
				break
		self.outputChoice.SetSelection(initial_idx)
		self.outputChoice.Bind(wx.EVT_CHOICE, self.onOutputTableChange)

		inp_choices = [t.displayName for t in self.input_tables]
		# Translators: Label for the Perkins input braille table choice in Add Secondary Braille Table dialog.
		self.inputChoice = sHelper.addLabeledControl(
			_("Perkins &input braille table:"), wx.Choice, choices=inp_choices
		)

		selected_out = self.output_tables[initial_idx].fileName if self.output_tables else ""
		inp_idx = _find_matching_input_table(selected_out, self.input_tables)
		self.inputChoice.SetSelection(inp_idx)

		btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
		if btn_sizer:
			main_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

		self.SetSizerAndFit(main_sizer)
		self.CenterOnParent()

	def onOutputTableChange(self, event: wx.Event) -> None:
		sel = self.outputChoice.GetSelection()
		if 0 <= sel < len(self.output_tables):
			out_file = self.output_tables[sel].fileName
			inp_idx = _find_matching_input_table(out_file, self.input_tables)
			self.inputChoice.SetSelection(inp_idx)

	def get_result(self) -> Tuple[str, str]:
		"""Return (output_table_filename, input_table_filename)."""
		out_sel = self.outputChoice.GetSelection()
		out_tbl = self.output_tables[out_sel].fileName if 0 <= out_sel < len(self.output_tables) else "fa-ir-g1.utb"

		inp_sel = self.inputChoice.GetSelection()
		inp_tbl = self.input_tables[inp_sel].fileName if 0 <= inp_sel < len(self.input_tables) else out_tbl

		return out_tbl, inp_tbl


class EditTableDialog(wx.Dialog):
	"""Modal dialog to adjust output and Perkins input braille tables."""

	def __init__(
		self,
		parent: wx.Window,
		*args: Any,
		available_output_tables: Optional[List[Any]] = None,
		available_input_tables: Optional[List[Any]] = None,
		**kwargs: Any,
	) -> None:
		# Flexible arg parsing: (current_out, current_inp) or (script_id, current_out, current_inp)
		if len(args) >= 3 and isinstance(args[0], str) and isinstance(args[1], str) and isinstance(args[2], str):
			current_out_table = args[1]
			current_inp_table = args[2]
			if len(args) >= 4 and available_output_tables is None:
				available_output_tables = args[3]
			if len(args) >= 5 and available_input_tables is None:
				available_input_tables = args[4]
		elif len(args) >= 2:
			current_out_table = args[0]
			current_inp_table = args[1]
			if len(args) >= 3 and available_output_tables is None:
				available_output_tables = args[2]
			if len(args) >= 4 and available_input_tables is None:
				available_input_tables = args[3]
		else:
			current_out_table = kwargs.get("current_out_table", "fa-ir-g1.utb")
			current_inp_table = kwargs.get("current_inp_table", "fa-ir-g1.utb")

		out_list = available_output_tables or []
		inp_list = available_input_tables or []

		table_names = {t.fileName: t.displayName for t in out_list}
		name = table_names.get(current_out_table, current_out_table)

		# Translators: Title of the Edit Table dialog
		super().__init__(parent, title=_("Configure Braille Table — %s") % name)

		self.output_tables = sorted(out_list, key=lambda t: t.displayName.lower())
		self.input_tables = sorted(inp_list, key=lambda t: t.displayName.lower())
		self.current_out_table = current_out_table
		self.current_inp_table = current_inp_table

		main_sizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=main_sizer)

		out_choices = [t.displayName for t in self.output_tables]
		# Translators: Label for the output braille table choice in Configure Braille Table dialog.
		self.outputChoice = sHelper.addLabeledControl(
			_("&Output braille table:"), wx.Choice, choices=out_choices
		)
		out_sel = 0
		for idx, t in enumerate(self.output_tables):
			if t.fileName == current_out_table:
				out_sel = idx
				break
		self.outputChoice.SetSelection(out_sel)
		self.outputChoice.Bind(wx.EVT_CHOICE, self.onOutputTableChange)

		inp_choices = [t.displayName for t in self.input_tables]
		# Translators: Label for the Perkins input braille table choice in Configure Braille Table dialog.
		self.inputChoice = sHelper.addLabeledControl(
			_("Perkins &input braille table:"), wx.Choice, choices=inp_choices
		)
		inp_sel = 0
		for idx, t in enumerate(self.input_tables):
			if t.fileName == current_inp_table:
				inp_sel = idx
				break
		self.inputChoice.SetSelection(inp_sel)

		btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
		if btn_sizer:
			main_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

		self.SetSizerAndFit(main_sizer)
		self.CenterOnParent()

	def onOutputTableChange(self, event: wx.Event) -> None:
		sel = self.outputChoice.GetSelection()
		if 0 <= sel < len(self.output_tables):
			out_file = self.output_tables[sel].fileName
			inp_idx = _find_matching_input_table(out_file, self.input_tables)
			self.inputChoice.SetSelection(inp_idx)

	def get_result(self) -> Tuple[str, str]:
		"""Return (output_table_filename, input_table_filename)."""
		out_sel = self.outputChoice.GetSelection()
		out_tbl = self.output_tables[out_sel].fileName if 0 <= out_sel < len(self.output_tables) else self.current_out_table

		inp_sel = self.inputChoice.GetSelection()
		inp_tbl = self.input_tables[inp_sel].fileName if 0 <= inp_sel < len(self.input_tables) else self.current_inp_table

		return out_tbl, inp_tbl


class AutoDetectWizardDialog(wx.Dialog):
	"""Modal dialog displaying detected Windows keyboards and candidate braille tables."""

	def __init__(
		self,
		parent: wx.Window,
		detection_result: Dict[str, Any],
		available_output_tables: List[Any],
		available_input_tables: List[Any],
	) -> None:
		# Translators: Title of the Auto-Detect Windows Keyboards setup wizard dialog
		super().__init__(parent, title=_("Auto-Detect Windows Keyboards"))

		self.available_output_tables = available_output_tables
		self.available_input_tables = available_input_tables
		self.tbl_names = {t.fileName: t.displayName for t in available_output_tables}
		self.candidates = list(detection_result.get("new_candidates", []))

		main_sizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=main_sizer)

		prim_info = detection_result.get("primary_info", {})
		prim_name = prim_info.get("lang_name", _("Primary"))
		prim_tbl = prim_info.get("table", "auto")
		prim_disp = self.tbl_names.get(prim_tbl, prim_tbl)

		# Translators: Label describing detected primary language in the auto-detect wizard
		prim_msg = _("Primary language (active): %s — %s") % (prim_name, prim_disp)
		prim_label = wx.StaticText(self, label=prim_msg)
		sHelper.addItem(prim_label)

		# Translators: Instructions above the list of detected secondary keyboards
		intro_label = wx.StaticText(self, label=_("Select which detected keyboard languages to add to your active braille tables:"))
		sHelper.addItem(intro_label)

		cand_choices = [self._format_candidate_label(c) for c in self.candidates]
		check_list_class = getattr(wx, "CheckListBox", wx.ListBox)
		self.checkList = sHelper.addLabeledControl(
			# Translators: Label for the checklist of detected keyboard languages
			_("&Detected keyboard languages:"), check_list_class, choices=cand_choices
		)

		if hasattr(self.checkList, "Check"):
			for i in range(len(self.candidates)):
				self.checkList.Check(i, True)
		if self.candidates:
			self.checkList.SetSelection(0)

		# Action buttons for editing selected candidate table
		btn_row = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: Button in setup wizard to customize the selected detected keyboard's braille table
		self.editBtn = wx.Button(self, label=_("&Edit Table..."))
		self.editBtn.Bind(wx.EVT_BUTTON, self.onEditCandidate)
		btn_row.Add(self.editBtn, 0, wx.RIGHT, 5)
		sHelper.addItem(btn_row)

		unsupported = detection_result.get("unsupported_layouts", [])
		if unsupported:
			unsupp_names = ", ".join(u.get("lang_name", "") for u in unsupported)
			# Translators: Note shown in wizard when some detected keyboards have no matching Liblouis table in NVDA
			unsupp_label = wx.StaticText(
				self,
				label=_("Note: No matching Liblouis braille table found in this NVDA installation for: %s") % unsupp_names
			)
			sHelper.addItem(unsupp_label)

		if hasattr(self, "CreateButtonSizer"):
			btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
			if btn_sizer:
				if hasattr(self, "FindWindowById"):
					ok_btn = self.FindWindowById(wx.ID_OK)
					if ok_btn and hasattr(ok_btn, "SetLabel"):
						# Translators: Confirmation button in setup wizard to add selected tables
						ok_btn.SetLabel(_("&Add Selected Tables"))
				main_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

		if hasattr(self, "SetSizerAndFit"):
			self.SetSizerAndFit(main_sizer)
		if hasattr(self, "CenterOnParent"):
			self.CenterOnParent()

	def _format_candidate_label(self, cand: Dict[str, Any]) -> str:
		out_tbl = cand.get("out_table", "")
		inp_tbl = cand.get("in_table", "")
		out_dn = self.tbl_names.get(out_tbl, out_tbl)
		inp_dn = self.tbl_names.get(inp_tbl, inp_tbl)
		lang_name = cand.get("lang_name", "")
		return f"{lang_name}: {out_dn} ({out_tbl})  —  Input: {inp_dn}"

	def onEditCandidate(self, event: wx.Event) -> None:
		sel = self.checkList.GetSelection()
		if sel == wx.NOT_FOUND or not (0 <= sel < len(self.candidates)):
			return
		cand = self.candidates[sel]
		dlg = EditTableDialog(
			self,
			cand["out_table"],
			cand["in_table"],
			available_output_tables=self.available_output_tables,
			available_input_tables=self.available_input_tables,
		)
		if dlg.ShowModal() == wx.ID_OK:
			new_out, new_inp = dlg.get_result()
			cand["out_table"] = new_out
			cand["in_table"] = new_inp
			new_label = self._format_candidate_label(cand)
			if hasattr(self.checkList, "SetString"):
				self.checkList.SetString(sel, new_label)
			if hasattr(self.checkList, "Check"):
				self.checkList.Check(sel, True)
		dlg.Destroy()

	def get_selected_tables(self) -> List[Tuple[str, str]]:
		"""Return list of (output_table_filename, input_table_filename) for selected items."""
		results = []
		for idx, cand in enumerate(self.candidates):
			is_selected = True
			if hasattr(self.checkList, "IsChecked"):
				is_selected = self.checkList.IsChecked(idx)
			elif hasattr(self.checkList, "IsSelected"):
				is_selected = self.checkList.IsSelected(idx)
			if is_selected:
				results.append((cand["out_table"], cand["in_table"]))
		return results


# Aliases for backward compatibility
AddLanguageDialog = AddTableDialog
EditLanguageDialog = EditTableDialog

