# coding: utf-8
"""Universal Multi-Script Liblouis Translation and Position Remapping for Auto Braille.

Handles translation of segmented text using dynamically resolved Liblouis tables for
Arabic/Persian, Cyrillic, Hebrew, Greek, Devanagari, and Latin writing systems,
stitching together braille cells and cursor routing positions across all NVDA-supported displays.
"""

from __future__ import annotations

import os
from typing import Callable, Dict, List, Optional, Set, Tuple

import brailleTables
import config
from logHandler import log
import louis

try:
	from . import scripts_data
	from . import segmenter
except ImportError:
	import scripts_data
	import segmenter

BRAILLE_PATTERNS = "braille-patterns.cti"

LEGACY_ENABLE_KEYS: Dict[str, str] = {
	"arabic_persian": "enableArabicPersian",
	"cyrillic": "enableCyrillic",
	"hebrew": "enableHebrew",
	"greek": "enableGreek",
	"indic_devanagari": "enableDevanagari",
}

LEGACY_TABLE_KEYS: Dict[str, str] = {
	"arabic_persian": "tableArabicPersian",
	"cyrillic": "tableCyrillic",
	"hebrew": "tableHebrew",
	"greek": "tableGreek",
	"indic_devanagari": "tableDevanagari",
}

_table_path_cache: Dict[str, str] = {}
_table_chain_cache: Dict[str, List[str]] = {}


def resolve_table_path(table_name: str) -> str:
	"""Resolve a table file name to an absolute file path registered in NVDA."""
	if not table_name:
		return ""
	if table_name in _table_path_cache:
		return _table_path_cache[table_name]

	# Sanitize table_name to avoid path traversal
	base_name = os.path.basename(table_name)

	# Check NVDA built-in tables directory
	path = os.path.join(brailleTables.TABLES_DIR, base_name)
	if os.path.isfile(path):
		_table_path_cache[table_name] = path
		return path

	# Check custom tables directories (NVDA 2024.3+)
	if hasattr(brailleTables, "_tablesDirs"):
		for directory in brailleTables._tablesDirs.values():
			candidate = os.path.join(directory, base_name)
			if os.path.isfile(candidate):
				_table_path_cache[table_name] = candidate
				return candidate

	_table_path_cache[table_name] = path
	return path


def get_table_chain_for_file(file_name: str) -> List[str]:
	"""Construct a Liblouis table chain containing the primary table and braille-patterns.cti."""
	if file_name in _table_chain_cache:
		return _table_chain_cache[file_name]

	primary = resolve_table_path(file_name)
	patterns = resolve_table_path(BRAILLE_PATTERNS)
	if os.path.isfile(patterns):
		chain = [primary, patterns]
	else:
		chain = [primary]

	_table_chain_cache[file_name] = chain
	return chain


def get_active_secondary_tables() -> List[str]:
	"""Return list of active secondary braille table filenames."""
	cfg = config.conf.get("autoBraille", {})
	raw_tables = cfg.get("activeTables")
	if raw_tables:
		if isinstance(raw_tables, str):
			return [t.strip() for t in raw_tables.split(",") if t.strip()]
		return list(raw_tables)

	# Fallback to activeLanguages if activeTables not yet configured
	raw_active = cfg.get("activeLanguages")
	if raw_active:
		if isinstance(raw_active, str):
			parts = [p.strip() for p in raw_active.split(",") if p.strip()]
		else:
			parts = list(raw_active)
		tables: List[str] = []
		for s_id in parts:
			tbl = cfg.get(f"table_{s_id}")
			if not tbl:
				info = scripts_data.get_script_info(s_id)
				tbl = info.default_output_table if info else "fa-ir-g1.utb"
			tables.append(tbl)
		return tables

	return ["fa-ir-g1.utb"]


def get_primary_table(active_tables: Optional[List[str]] = None) -> str:
	"""Return the primary output table filename."""
	cfg = config.conf.get("autoBraille", {})
	tbl = cfg.get("primaryTable", "auto")
	if tbl and tbl != "auto":
		return tbl
	if active_tables:
		return os.path.basename(active_tables[0])
	try:
		nvda_tbl = config.conf["braille"]["translationTable"]
		if nvda_tbl and nvda_tbl != "auto":
			return nvda_tbl
	except Exception:
		pass
	return "en-ueb-g1.ctb"


def get_primary_script(active_tables: Optional[List[str]] = None) -> str:
	"""Return the script ID corresponding to the primary output table."""
	cfg = config.conf.get("autoBraille", {})
	lang_cfg = cfg.get("primaryLanguage")
	if lang_cfg and lang_cfg != "auto" and scripts_data.get_script_info(lang_cfg):
		return lang_cfg

	prim_table = get_primary_table(active_tables)
	s_info = scripts_data.resolve_table_to_script(prim_table)
	return s_info.id if s_info else "latin"


def get_enabled_scripts(active_tables: Optional[List[str]] = None) -> Set[str]:
	"""Return the set of currently enabled scripts from active tables."""
	primary = get_primary_script(active_tables)
	enabled: Set[str] = {primary}

	sec_tables = get_active_secondary_tables()
	for tbl in sec_tables:
		s = scripts_data.resolve_table_to_script(tbl)
		if s:
			enabled.add(s.id)

	return enabled


def get_script_table_chain(script_name: str, active_tables: List[str]) -> List[str]:
	"""Get the Liblouis table chain for a given script based on active tables."""
	primary = get_primary_script(active_tables)

	if script_name == primary:
		cfg = config.conf.get("autoBraille", {})
		configured = cfg.get("primaryTable", "auto")
		if configured and configured != "auto":
			return get_table_chain_for_file(configured)
		if active_tables:
			return list(active_tables)
		info = scripts_data.get_script_info(primary)
		default_tbl = info.default_output_table if info else "en-ueb-g1.ctb"
		return get_table_chain_for_file(default_tbl)

	# Check active secondary tables
	sec_tables = get_active_secondary_tables()
	for tbl in sec_tables:
		s = scripts_data.resolve_table_to_script(tbl)
		if s and s.id == script_name:
			return get_table_chain_for_file(tbl)

	# Fallback to configured script key or default
	cfg = config.conf.get("autoBraille", {})
	configured = cfg.get(f"table_{script_name}")
	if not configured or configured == "auto":
		info = scripts_data.get_script_info(script_name)
		configured = info.default_output_table if info else "fa-ir-g1.utb"

	return get_table_chain_for_file(configured)


def segment_with_doc_langs(
	inbuf: str,
	doc_lang_spans: Optional[List[Tuple[int, int, str]]],
	enabled_scripts: Set[str],
	primary_script: str,
) -> List[Tuple[str, int, int, str]]:
	"""Segment text respecting official document language tags when accurate, falling back to script detection."""
	if not inbuf:
		return []
	if not doc_lang_spans:
		return segmenter.segment_text(inbuf, enabled_scripts=enabled_scripts, primary_script=primary_script)

	text_len = len(inbuf)
	raw_spans: List[Tuple[int, int, Optional[str]]] = []
	last_pos = 0

	for s_start, s_end, lang in sorted(doc_lang_spans, key=lambda x: x[0]):
		s_start = max(0, min(s_start, text_len))
		s_end = max(0, min(s_end, text_len))
		if s_start > last_pos:
			raw_spans.append((last_pos, s_start, None))
		if s_end > s_start:
			raw_spans.append((s_start, s_end, lang))
			last_pos = s_end
	if last_pos < text_len:
		raw_spans.append((last_pos, text_len, None))

	segments: List[Tuple[str, int, int, str]] = []
	for start, end, lang in raw_spans:
		chunk = inbuf[start:end]
		if not chunk:
			continue
		s_info = scripts_data.resolve_doc_lang_to_script(lang) if lang else None
		if s_info and scripts_data.is_script_compatible(chunk, s_info.id):
			segments.append((chunk, start, end, s_info.id))
		else:
			sub_segs = segmenter.segment_text(chunk, enabled_scripts=enabled_scripts, primary_script=primary_script)
			for sub_text, sub_start, sub_end, sub_script in sub_segs:
				segments.append((sub_text, start + sub_start, start + sub_end, sub_script))

	if not segments:
		return [(inbuf, 0, text_len, primary_script)]

	merged: List[Tuple[str, int, int, str]] = [segments[0]]
	for text, start, end, script in segments[1:]:
		prev_text, prev_start, prev_end, prev_script = merged[-1]
		if script == prev_script and start == prev_end:
			merged[-1] = (prev_text + text, prev_start, end, script)
		else:
			merged.append((text, start, end, script))

	return merged


def multi_script_translate(
	original_translate: Callable[..., Tuple[List[int], List[int], List[int], Optional[int]]],
	active_tables: List[str],
	inbuf: str,
	typeform: Optional[List[int]] = None,
	mode: int = 0,
	cursorPos: Optional[int] = None,
	doc_lang_spans: Optional[List[Tuple[int, int, str]]] = None,
) -> Tuple[List[int], List[int], List[int], Optional[int]]:
	"""Translate mixed-script text by segmenting and re-mapping cursor and routing positions."""
	primary_script = get_primary_script(active_tables)
	enabled_scripts = get_enabled_scripts(active_tables)
	honor_doc = config.conf.get("autoBraille", {}).get("honorDocumentLang", True)
	tactile_marker = config.conf.get("autoBraille", {}).get("tactileMarker", "none")

	try:
		if honor_doc and doc_lang_spans:
			segments = segment_with_doc_langs(
				inbuf, doc_lang_spans, enabled_scripts=enabled_scripts, primary_script=primary_script
			)
		else:
			segments = segmenter.segment_text(
				inbuf, enabled_scripts=enabled_scripts, primary_script=primary_script
			)
	except Exception:
		log.warning("Auto Braille segmentation failed; falling back to single table", exc_info=True)
		return original_translate(active_tables, inbuf, typeform=typeform, mode=mode, cursorPos=cursorPos)

	if len(segments) <= 1:
		seg_script = segments[0][3] if segments else primary_script
		table = get_script_table_chain(seg_script, active_tables)
		try:
			cells, b2r, r2b, cur = original_translate(table, inbuf, typeform=typeform, mode=mode, cursorPos=cursorPos)
			if cells and seg_script != primary_script:
				if tactile_marker == "dot8_first":
					cells = [cells[0] | 0x80] + cells[1:]
				elif tactile_marker == "dot7_first":
					cells = [cells[0] | 0x40] + cells[1:]
				elif tactile_marker == "dots78_secondary":
					cells = [c | 0xC0 for c in cells]
			return cells, b2r, r2b, cur
		except Exception:
			return original_translate(active_tables, inbuf, typeform=typeform, mode=mode, cursorPos=cursorPos)

	all_cells: List[int] = []
	all_b2r: List[int] = []
	all_r2b: List[int] = []
	final_cursor_pos: Optional[int] = None
	text_len = len(inbuf)

	# Cache table chains per script for the current line to minimize lookups
	chains_by_script: Dict[str, List[str]] = {}

	for idx, (seg_text, start_idx, end_idx, script) in enumerate(segments):
		if script not in chains_by_script:
			chains_by_script[script] = get_script_table_chain(script, active_tables)
		table = chains_by_script[script]

		# Local cursor calculation
		seg_cursor: Optional[int] = None
		seg_mode = mode
		if cursorPos is not None:
			if start_idx <= cursorPos < end_idx:
				seg_cursor = cursorPos - start_idx
			elif cursorPos == end_idx and end_idx == text_len:
				seg_cursor = len(seg_text)
			else:
				if hasattr(louis, "compbrlAtCursor"):
					seg_mode = mode & ~louis.compbrlAtCursor

		seg_typeform = typeform[start_idx:end_idx] if typeform is not None else None

		try:
			cells, b2r, r2b, cur = original_translate(
				table,
				seg_text,
				typeform=seg_typeform,
				mode=seg_mode,
				cursorPos=seg_cursor,
			)
		except Exception:
			log.warning(
				"Auto Braille translation failed on script %r (table %r); falling back",
				script,
				table,
				exc_info=True,
			)
			return original_translate(active_tables, inbuf, typeform=typeform, mode=mode, cursorPos=cursorPos)

		# Apply tactile marker if configured
		if cells:
			if tactile_marker == "dot8_first" and idx > 0 and script != segments[idx - 1][3]:
				cells = [cells[0] | 0x80] + cells[1:]
			elif tactile_marker == "dot7_first" and idx > 0 and script != segments[idx - 1][3]:
				cells = [cells[0] | 0x40] + cells[1:]
			elif tactile_marker == "dots78_secondary" and script != primary_script:
				cells = [c | 0xC0 for c in cells]

		cell_offset = len(all_cells)
		all_cells.extend(cells)

		# Remap positions for cursor routing keys (cells -> raw characters)
		for p in b2r:
			all_b2r.append(start_idx + p)

		# Remap positions for caret / focus cursor (raw characters -> cells)
		for p in r2b:
			all_r2b.append(cell_offset + p)

		# Track cursor position
		if cur is not None and final_cursor_pos is None:
			final_cursor_pos = cell_offset + cur

	# Resolve and clamp braille cursor position strictly to prevent LookupError
	if cursorPos is not None:
		if final_cursor_pos is None:
			if cursorPos >= text_len:
				final_cursor_pos = len(all_cells)
			elif cursorPos < len(all_r2b):
				final_cursor_pos = all_r2b[cursorPos]
			else:
				final_cursor_pos = len(all_cells)

		if len(all_cells) == 0:
			final_cursor_pos = None
		elif final_cursor_pos is not None:
			final_cursor_pos = max(0, min(final_cursor_pos, len(all_cells)))
	else:
		final_cursor_pos = None

	return all_cells, all_b2r, all_r2b, final_cursor_pos
