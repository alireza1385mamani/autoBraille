# coding: utf-8
"""Perkins Braille Keyboard Input Synchronizer for Auto Braille.

Automatically synchronizes the active braille input table (used by Perkins braille keys
on HIMS Braille Edge and other braille displays) with the active Windows keyboard layout / input language.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Dict, List, Optional

import api
import brailleInput
import brailleTables
import config
from logHandler import log
import ui

try:
	_ = _  # type: ignore
except NameError:
	try:
		from addonHandler import initTranslation
		initTranslation()
	except Exception:
		_ = lambda s: s

try:
	from . import scripts_data, translator
except ImportError:
	import scripts_data, translator

# Configure explicit 64-bit ctypes prototypes for Windows user32 APIs
try:
	user32 = ctypes.windll.user32
	user32.GetForegroundWindow.restype = wintypes.HWND
	user32.GetForegroundWindow.argtypes = []

	user32.GetWindowThreadProcessId.restype = wintypes.DWORD
	user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]

	hkl_type = getattr(wintypes, "HKL", ctypes.c_void_p)
	user32.GetKeyboardLayout.restype = hkl_type
	user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
except Exception:
	user32 = getattr(ctypes.windll, "user32", None)

LEGACY_INPUT_ENABLE_KEYS: Dict[str, str] = {
	"arabic_persian": "enableArabicPersianInput",
	"cyrillic": "enableCyrillicInput",
	"hebrew": "enableHebrewInput",
	"greek": "enableGreekInput",
	"indic_devanagari": "enableDevanagariInput",
}

LEGACY_INPUT_TABLE_KEYS: Dict[str, str] = {
	"arabic_persian": "inputTableArabicPersian",
	"cyrillic": "inputTableCyrillic",
	"hebrew": "inputTableHebrew",
	"greek": "inputTableGreek",
	"indic_devanagari": "inputTableDevanagari",
}

_last_lang_id: Optional[int] = None
_last_table_name: Optional[str] = None
_lang_table_cache: Dict[int, str] = {}


def invalidate_cache() -> None:
	"""Clear cached table mappings when configuration changes."""
	global _last_lang_id, _last_table_name, _lang_table_cache
	_last_lang_id = None
	_last_table_name = None
	_lang_table_cache.clear()


def get_foreground_keyboard_layout() -> int:
	"""Retrieve the HKL keyboard layout identifier for the current foreground window thread."""
	if not user32:
		return 0
	try:
		hwnd = user32.GetForegroundWindow()
		if not hwnd:
			return 0
		pid = wintypes.DWORD()
		thread_id = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
		if not thread_id:
			return 0
		hkl = user32.GetKeyboardLayout(thread_id)
		val = ctypes.cast(hkl, ctypes.c_void_p).value
		return (val or 0) & 0xFFFFFFFF
	except Exception:
		return 0


def get_current_input_lang_id() -> int:
	"""Return the active 16-bit LANGID (language identifier) of the focused application."""
	hkl = get_foreground_keyboard_layout()
	return hkl & 0xFFFF


def resolve_concrete_table_name(table_name: str, is_input: bool = True) -> str:
	"""Ensure table name is not 'auto', resolving to a concrete Liblouis table file."""
	if not table_name or table_name == "auto":
		if hasattr(brailleTables, "getDefaultTableForCurLang"):
			try:
				t_type = brailleTables.TableType.INPUT if is_input else brailleTables.TableType.OUTPUT
				resolved = brailleTables.getDefaultTableForCurLang(t_type)
				if resolved and resolved != "auto":
					return resolved
			except Exception:
				pass
		try:
			conf_table = config.conf["braille"]["inputTable"]
			if conf_table and conf_table != "auto":
				return conf_table
		except Exception:
			pass
		return "en-ueb-g1.ctb"
	return table_name


def resolve_input_table_for_lang(lang_id: int) -> str:
	"""Map a Windows LANGID to the appropriate configured braille input table."""
	cfg = config.conf.get("autoBraille", {})
	primary_script = translator.get_primary_script()

	# Check full LANGID first, then primary language ID (low 10 bits)
	script_id = scripts_data.LANG_ID_TO_SCRIPT.get(lang_id)
	if not script_id:
		primary_lang = lang_id & 0x03FF
		script_id = scripts_data.LANG_ID_TO_SCRIPT.get(primary_lang)

	# If layout matches primary script or unknown, return Primary input table
	if script_id == primary_script:
		primary_configured = cfg.get("primaryInputTable", "auto")
		if not primary_configured or primary_configured == "auto":
			info = scripts_data.get_script_info(primary_script)
			fallback = info.default_input_table if info else "en-ueb-g1.ctb"
			return resolve_concrete_table_name(fallback, is_input=True)
		return resolve_concrete_table_name(primary_configured, is_input=True)

	# If layout matches a secondary script, check active secondary tables
	if script_id:
		raw_tables = cfg.get("activeTables")
		if raw_tables:
			sec_tables = [t.strip() for t in raw_tables.split(",") if t.strip()] if isinstance(raw_tables, str) else list(raw_tables)
			for tbl in sec_tables:
				s_info = scripts_data.resolve_table_to_script(tbl)
				if s_info and s_info.id == script_id:
					inp_tbl = cfg.get(f"inputTable_{tbl}")
					if not inp_tbl or inp_tbl == "auto":
						inp_tbl = s_info.default_input_table
					return resolve_concrete_table_name(inp_tbl, is_input=True)

		# Fallback to legacy activeLanguages
		raw_active = cfg.get("activeLanguages")
		if raw_active:
			active_set = {p.strip() for p in raw_active.split(",") if p.strip()} if isinstance(raw_active, str) else set(raw_active)
			if script_id in active_set:
				info = scripts_data.get_script_info(script_id)
				configured = cfg.get(f"input_table_{script_id}")
				if not configured or configured == "auto":
					configured = info.default_input_table if info else "fa-ir-g1.utb"
				return resolve_concrete_table_name(configured, is_input=True)

	# Fallback: Primary input table
	primary_configured = cfg.get("primaryInputTable", "auto")
	if not primary_configured or primary_configured == "auto":
		info = scripts_data.get_script_info(primary_script)
		fallback = info.default_input_table if info else "en-ueb-g1.ctb"
		return resolve_concrete_table_name(fallback, is_input=True)
	return resolve_concrete_table_name(primary_configured, is_input=True)


def sync_input_table(force: bool = False) -> bool:
	"""Synchronize brailleInput.handler.table with the active Windows keyboard layout.

	Returns True if the table was changed.
	"""
	# Instant exit if braille input subsystem is not active (e.g. during startup or no display)
	if not brailleInput.handler:
		return False

	cfg = config.conf.get("autoBraille", {})
	if not cfg.get("autoSyncInputTable", True) and not force:
		return False

	lang_id = get_current_input_lang_id()
	if not lang_id:
		return False

	global _last_lang_id, _last_table_name
	current_table = getattr(brailleInput.handler, "table", None)
	current_file = getattr(current_table, "fileName", "")

	# Fast path: skip resolution if language is unchanged and table is already in sync
	if not force and lang_id == _last_lang_id and current_file == _last_table_name:
		return False

	target_table_name = _lang_table_cache.get(lang_id)
	if target_table_name is None or force:
		target_table_name = resolve_input_table_for_lang(lang_id)
		if not target_table_name or target_table_name == "auto":
			target_table_name = "en-ueb-g1.ctb"
		_lang_table_cache[lang_id] = target_table_name

	if current_file == target_table_name:
		_last_lang_id = lang_id
		_last_table_name = target_table_name
		return False

	try:
		new_table = brailleTables.getTable(target_table_name)
		brailleInput.handler.table = new_table
		_last_lang_id = lang_id
		_last_table_name = target_table_name
		log.info(
			"Auto Braille: switched input table from %r to %r (LANGID: 0x%04X)",
			current_file,
			target_table_name,
			lang_id,
		)
		return True
	except Exception:
		log.warning(
			"Auto Braille: failed to set input table to %r for LANGID 0x%04X",
			target_table_name,
			lang_id,
			exc_info=True,
		)
		return False


def toggle_input_language() -> None:
	"""Cycle braille input language manually across active languages."""
	global _last_table_name
	if not brailleInput.handler:
		return

	cfg = config.conf.get("autoBraille", {})
	current_table = getattr(brailleInput.handler, "table", None)
	current_file = getattr(current_table, "fileName", "")

	primary_script = cfg.get("primaryLanguage", "latin")
	primary_info = scripts_data.get_script_info(primary_script)
	primary_default = primary_info.default_input_table if primary_info else "en-ueb-g1.ctb"
	primary_cfg = cfg.get("primaryInputTable", "auto")
	primary_table = resolve_concrete_table_name(
		primary_cfg if primary_cfg and primary_cfg != "auto" else primary_default, is_input=True
	)

	# Build ordered list of unique input tables: Primary followed by each active secondary language
	table_candidates: List[str] = [primary_table]

	raw_tables = cfg.get("activeTables")
	if raw_tables:
		sec_tables = [t.strip() for t in raw_tables.split(",") if t.strip()] if isinstance(raw_tables, str) else list(raw_tables)
		for tbl in sec_tables:
			inp_tbl = cfg.get(f"inputTable_{tbl}")
			if not inp_tbl or inp_tbl == "auto":
				s_info = scripts_data.resolve_table_to_script(tbl)
				inp_tbl = s_info.default_input_table if s_info else tbl
			concrete = resolve_concrete_table_name(inp_tbl, is_input=True)
			if concrete and concrete not in table_candidates:
				table_candidates.append(concrete)
	else:
		raw_active = cfg.get("activeLanguages")
		if raw_active:
			if isinstance(raw_active, str):
				active_ids = [p.strip() for p in raw_active.split(",") if p.strip()]
			else:
				active_ids = list(raw_active)
		else:
			active_ids = ["arabic_persian"] if primary_script == "latin" else ["latin"]

		for s_id in active_ids:
			if s_id == primary_script:
				continue
			info = scripts_data.get_script_info(s_id)
			if not info:
				continue
			tbl = cfg.get(f"input_table_{s_id}")
			if not tbl:
				legacy_key = LEGACY_INPUT_TABLE_KEYS.get(s_id)
				tbl = cfg.get(legacy_key, info.default_input_table) if legacy_key else info.default_input_table
			concrete = resolve_concrete_table_name(tbl, is_input=True)
			if concrete and concrete not in table_candidates:
				table_candidates.append(concrete)

	if len(table_candidates) <= 1:
		alt_script = "fa-ir-g1.utb" if primary_script == "latin" else "en-ueb-g1.ctb"
		fallback_alt = resolve_concrete_table_name(alt_script, is_input=True)
		if fallback_alt not in table_candidates:
			table_candidates.append(fallback_alt)

	# Find next table in cycle
	if current_file in table_candidates:
		cur_idx = table_candidates.index(current_file)
		next_idx = (cur_idx + 1) % len(table_candidates)
	else:
		next_idx = 1 if len(table_candidates) > 1 else 0

	target = table_candidates[next_idx]

	try:
		new_table = brailleTables.getTable(target)
		brailleInput.handler.table = new_table
		_last_table_name = target
		# Translators: Announcement when input braille table is switched
		ui.message(_("Braille input: %s") % new_table.displayName)
	except Exception:
		log.warning("Auto Braille: failed to toggle input table to %r", target, exc_info=True)
