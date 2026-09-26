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

	user32.GetKeyboardLayoutList.restype = wintypes.INT
	user32.GetKeyboardLayoutList.argtypes = [wintypes.INT, ctypes.POINTER(hkl_type)]
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


def get_installed_system_keyboard_layouts() -> List[int]:
	"""Retrieve all unique 16-bit LANGIDs for keyboard layouts installed on the system.

	Uses 64-bit safe GetKeyboardLayoutList as primary in-memory source,
	and safely reads HKCU\\Keyboard Layout\\Preload as a read-only fallback.
	"""
	lang_ids: List[int] = []
	seen = set()

	# 1. Primary in-memory detection via Win32 GetKeyboardLayoutList
	if user32 and hasattr(user32, "GetKeyboardLayoutList"):
		try:
			count = user32.GetKeyboardLayoutList(0, None)
			if count > 0:
				hkl_type = getattr(wintypes, "HKL", ctypes.c_void_p)
				hkls = (hkl_type * count)()
				ret = user32.GetKeyboardLayoutList(count, hkls)
				for i in range(ret):
					val = ctypes.cast(hkls[i], ctypes.c_void_p).value
					if val:
						lid = val & 0xFFFF
						if lid and lid not in seen:
							seen.add(lid)
							lang_ids.append(lid)
		except Exception as e:
			log.debug(f"AutoBraille: GetKeyboardLayoutList failed: {e}")

	# 2. Secondary read-only fallback via Windows Registry Preload
	try:
		import winreg
		import re
		hex_pat = re.compile(r"^[0-9a-fA-F]{1,8}$")
		with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Keyboard Layout\Preload", 0, winreg.KEY_READ) as key:
			idx = 0
			while True:
				try:
					val_name, val_data, _ = winreg.EnumValue(key, idx)
					idx += 1
					if isinstance(val_data, str) and hex_pat.match(val_data):
						lid = int(val_data, 16) & 0xFFFF
						if lid and lid not in seen:
							seen.add(lid)
							lang_ids.append(lid)
				except OSError:
					break
	except Exception:
		pass

	return lang_ids


def get_keyboard_language_name(lang_id: int) -> str:
	"""Return a friendly language name for a Windows LANGID."""
	try:
		kernel32 = getattr(ctypes.windll, "kernel32", None)
		if kernel32:
			buf = ctypes.create_unicode_buffer(128)
			# 0x0002 = LOCALE_SLOCALIZEDLANGUAGENAME
			ret = kernel32.GetLocaleInfoW(lang_id, 0x0002, buf, 128)
			if ret > 0 and buf.value.strip():
				return buf.value.strip()
			# 0x1001 = LOCALE_SENGLANGUAGENAME
			ret = kernel32.GetLocaleInfoW(lang_id, 0x1001, buf, 128)
			if ret > 0 and buf.value.strip():
				return buf.value.strip()
	except Exception:
		pass

	tbl = scripts_data.LANG_ID_TO_TABLE.get(lang_id) or scripts_data.LANG_ID_TO_TABLE.get(lang_id & 0x03FF)
	if tbl:
		return scripts_data.get_language_name_for_table(tbl)

	script_id = scripts_data.LANG_ID_TO_SCRIPT.get(lang_id) or scripts_data.LANG_ID_TO_SCRIPT.get(lang_id & 0x03FF)
	if script_id:
		s_info = scripts_data.get_script_info(script_id)
		if s_info:
			return s_info.name

	return f"Language (0x{lang_id:04X})"


def detect_keyboard_tables(
	available_output_tables: Optional[List[Any]] = None,
	available_input_tables: Optional[List[Any]] = None,
	primary_table: Optional[str] = None,
	existing_tables: Optional[List[str]] = None,
) -> Dict[str, Any]:
	"""Detect installed Windows keyboards and resolve to candidate Liblouis tables."""
	if primary_table is None or primary_table == "auto":
		primary_table = translator.get_primary_table()
	primary_script = translator.get_primary_script()

	if existing_tables is None:
		existing_tables = translator.get_active_secondary_tables()
	existing_set = set(existing_tables)

	detected_lids = get_installed_system_keyboard_layouts()
	if not detected_lids:
		cur_lid = get_current_input_lang_id()
		if cur_lid:
			detected_lids = [cur_lid]

	primary_lid = None
	primary_name = scripts_data.get_language_name_for_table(primary_table)

	new_candidates: List[Dict[str, Any]] = []
	unsupported_layouts: List[Dict[str, Any]] = []
	seen_out_tables = set(existing_tables)
	seen_out_tables.add(primary_table)

	# 1. Identify which detected layout matches Primary Table
	for lid in detected_lids:
		mapped_tbl = scripts_data.LANG_ID_TO_TABLE.get(lid) or scripts_data.LANG_ID_TO_TABLE.get(lid & 0x03FF)
		mapped_script = scripts_data.LANG_ID_TO_SCRIPT.get(lid) or scripts_data.LANG_ID_TO_SCRIPT.get(lid & 0x03FF)
		if mapped_tbl == primary_table or (mapped_script and mapped_script == primary_script):
			primary_lid = lid
			primary_name = get_keyboard_language_name(lid)
			break

	if primary_lid is None and detected_lids:
		primary_lid = detected_lids[0]

	# 2. Process secondary candidates
	for lid in detected_lids:
		lang_name = get_keyboard_language_name(lid)

		# Skip if it is the primary language layout
		if lid == primary_lid:
			continue

		# 3-Tier table resolution
		cand_tbl = scripts_data.LANG_ID_TO_TABLE.get(lid)
		if not cand_tbl:
			cand_tbl = scripts_data.LANG_ID_TO_TABLE.get(lid & 0x03FF)
		cand_script = scripts_data.LANG_ID_TO_SCRIPT.get(lid) or scripts_data.LANG_ID_TO_SCRIPT.get(lid & 0x03FF)
		if not cand_tbl and cand_script:
			s_info = scripts_data.get_script_info(cand_script)
			if s_info:
				cand_tbl = s_info.default_output_table

		if not cand_tbl:
			unsupported_layouts.append({"lang_id": lid, "lang_name": lang_name})
			continue

		# Validate against available Liblouis catalog
		valid_out = scripts_data.validate_table_available(cand_tbl, available_output_tables)
		if not valid_out:
			unsupported_layouts.append({"lang_id": lid, "lang_name": lang_name})
			continue

		# Check if already configured or duplicate
		if valid_out in seen_out_tables:
			continue

		# Resolve matching Perkins input table
		inp_tbl = scripts_data.find_best_input_table(valid_out, available_input_tables)

		seen_out_tables.add(valid_out)
		new_candidates.append({
			"lang_id": lid,
			"lang_name": lang_name,
			"out_table": valid_out,
			"in_table": inp_tbl,
			"script_id": cand_script or scripts_data.resolve_table_to_script(valid_out).id,
		})

	return {
		"primary_info": {
			"lang_id": primary_lid,
			"lang_name": primary_name,
			"table": primary_table,
		},
		"new_candidates": new_candidates,
		"existing_tables": list(existing_tables),
		"unsupported_layouts": unsupported_layouts,
	}


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
	primary_tbl = translator.get_primary_table()
	primary_script = translator.get_primary_script()
	sec_tables = translator.get_active_secondary_tables()

	# 1. First check if exact LANGID or primary language has an intra-script table mapping
	exact_tbl = scripts_data.LANG_ID_TO_TABLE.get(lang_id)
	if not exact_tbl:
		exact_tbl = scripts_data.LANG_ID_TO_TABLE.get(lang_id & 0x03FF)

	if exact_tbl:
		# If it matches primary table, return primary input table
		if exact_tbl == primary_tbl or exact_tbl.split("-")[0] == primary_tbl.split("-")[0]:
			primary_configured = cfg.get("primaryInputTable", "auto")
			if not primary_configured or primary_configured == "auto":
				info = scripts_data.get_script_info(primary_script)
				fallback = info.default_input_table if info else exact_tbl
				return resolve_concrete_table_name(fallback, is_input=True)
			return resolve_concrete_table_name(primary_configured, is_input=True)

		# If it matches an active secondary table, use that table's input mapping
		for tbl in sec_tables:
			if tbl == exact_tbl or tbl.split("-")[0] == exact_tbl.split("-")[0]:
				inp_tbl = cfg.get(f"inputTable_{tbl}")
				if not inp_tbl or inp_tbl == "auto":
					inp_tbl = tbl
				return resolve_concrete_table_name(inp_tbl, is_input=True)

	# 2. Check script ID level mapping
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
		for tbl in sec_tables:
			s_info = scripts_data.resolve_table_to_script(tbl)
			if s_info and s_info.id == script_id:
				inp_tbl = cfg.get(f"inputTable_{tbl}")
				if not inp_tbl or inp_tbl == "auto":
					inp_tbl = tbl
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
