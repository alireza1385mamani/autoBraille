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

# Standard 8-dot braille pin bitmasks (ISO/TR 11548-1)
BRAILLE_DOT_7: int = 0x40        # Lower-left dot (Pin 7)
BRAILLE_DOT_8: int = 0x80        # Lower-right dot (Pin 8)
BRAILLE_DOTS_7_8: int = 0xC0     # Underline indicator (Pins 7 and 8)

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


def get_default_secondary_table(primary_tbl: Optional[str] = None) -> str:
	"""Determine sensible default secondary table based on the primary table."""
	if not primary_tbl:
		primary_tbl = get_primary_table()
	s = scripts_data.resolve_table_to_script(primary_tbl)
	if s and s.id != "latin":
		return "en-ueb-g1.ctb"
	return "fa-ir-g1.utb"


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

	prim = get_primary_table()
	return [get_default_secondary_table(prim)]


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


def get_candidate_tables_for_script(script_name: str, active_tables: Optional[List[str]] = None) -> List[str]:
	"""Get all active tables for a given script in priority order (primary first if matching)."""
	primary_script = get_primary_script(active_tables)
	candidates: List[str] = []
	if script_name == primary_script:
		prim_tbl = get_primary_table(active_tables)
		if prim_tbl:
			candidates.append(prim_tbl)

	sec_tables = get_active_secondary_tables()
	for tbl in sec_tables:
		s = scripts_data.resolve_table_to_script(tbl)
		if s and s.id == script_name and tbl not in candidates:
			candidates.append(tbl)

	if not candidates:
		info = scripts_data.get_script_info(script_name)
		default_tbl = info.default_output_table if info else "en-ueb-g1.ctb"
		candidates.append(default_tbl)

	return candidates


def get_script_table_chain(
	script_name: str,
	active_tables: List[str],
	text_sample: str = "",
	doc_table: Optional[str] = None,
) -> List[str]:
	"""Get the Liblouis table chain for a given script, performing intra-script disambiguation if multiple tables exist."""
	if doc_table:
		return get_table_chain_for_file(doc_table)

	candidates = get_candidate_tables_for_script(script_name, active_tables)
	if len(candidates) == 1 or not text_sample:
		return get_table_chain_for_file(candidates[0])

	chosen = scripts_data.detect_intra_script_table(text_sample, candidates)
	target = chosen if chosen else candidates[0]
	return get_table_chain_for_file(target)


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

	tagged_segments: List[Tuple[str, int, int, str, Optional[str]]] = []
	for start, end, lang in raw_spans:
		chunk = inbuf[start:end]
		if not chunk:
			continue
		s_info = scripts_data.resolve_doc_lang_to_script(lang) if lang else None
		if s_info and scripts_data.is_script_compatible(chunk, s_info.id):
			tagged_segments.append((chunk, start, end, s_info.id, lang))
		else:
			sub_segs = segmenter.segment_text(chunk, enabled_scripts=enabled_scripts, primary_script=primary_script)
			for sub_text, sub_start, sub_end, sub_script in sub_segs:
				tagged_segments.append((sub_text, start + sub_start, start + sub_end, sub_script, None))

	if not tagged_segments:
		return [(inbuf, 0, text_len, primary_script)]

	merged_tagged: List[Tuple[str, int, int, str, Optional[str]]] = [tagged_segments[0]]
	for text, start, end, script, lang in tagged_segments[1:]:
		prev_text, prev_start, prev_end, prev_script, prev_lang = merged_tagged[-1]
		prev_tbl = scripts_data.resolve_doc_lang_to_table(prev_lang) if prev_lang else None
		curr_tbl = scripts_data.resolve_doc_lang_to_table(lang) if lang else None
		if script == prev_script and prev_tbl == curr_tbl and start == prev_end:
			merged_tagged[-1] = (prev_text + text, prev_start, end, script, prev_lang)
		else:
			merged_tagged.append((text, start, end, script, lang))

	return [(t, s, e, sc) for t, s, e, sc, _ in merged_tagged]


def resolve_segment_table(
	seg_text: str,
	start_idx: int,
	end_idx: int,
	script: str,
	active_tables: List[str],
	doc_lang_spans: Optional[List[Tuple[int, int, str]]] = None,
	full_inbuf: str = "",
) -> List[str]:
	"""Determine the exact table chain for a segment based on doc markup, candidate tables, and text."""
	target_chain: Optional[List[str]] = None

	if doc_lang_spans:
		for s_start, s_end, lang in doc_lang_spans:
			if lang and (s_start <= start_idx < s_end or s_start < end_idx <= s_end):
				doc_tbl = scripts_data.resolve_doc_lang_to_table(lang)
				if doc_tbl:
					tbl_script = scripts_data.resolve_table_to_script(doc_tbl)
					if tbl_script and tbl_script.id == script:
						target_chain = get_table_chain_for_file(doc_tbl)
						break

	if not target_chain:
		target_chain = get_script_table_chain(script, active_tables, text_sample=seg_text)

	# Boundary Guarding for Grade 2 Contracted Braille
	cfg = config.conf.get("autoBraille", {})
	if cfg.get("grade2BoundaryGuard", True) and target_chain:
		target_file = os.path.basename(target_chain[0]).lower()
		if scripts_data.is_contracted_table(target_file):
			needs_g1_fallback = False

			# Guard 1: Single-letter word-sign protection (e.g. 'b' -> 'but', 'c' -> 'can')
			if scripts_data.is_single_letter_wordsign_candidate(seg_text):
				needs_g1_fallback = True

			# Guard 2: Technical identifiers, code symbols, paths, and camelCase
			elif scripts_data.is_technical_identifier(seg_text):
				needs_g1_fallback = True

			# Guard 3: Numeric mode boundary lookback (e.g. '123b' or '۱۲۳a')
			elif full_inbuf and start_idx > 0:
				prev_char = full_inbuf[start_idx - 1]
				if (prev_char.isdigit() or prev_char in "۰۱۲۳۴۵۶۷۸۹") and seg_text and seg_text[0].isalnum():
					needs_g1_fallback = True

			if needs_g1_fallback:
				g1_companion = scripts_data.get_grade1_companion_table(target_file)
				if g1_companion:
					return get_table_chain_for_file(g1_companion)

	return target_chain


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
	primary_chain = get_script_table_chain(primary_script, active_tables)

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
		start_idx = segments[0][1] if segments else 0
		end_idx = segments[0][2] if segments else len(inbuf)
		table = resolve_segment_table(inbuf, start_idx, end_idx, seg_script, active_tables, doc_lang_spans, full_inbuf=inbuf)
		try:
			cells, b2r, r2b, cur = original_translate(table, inbuf, typeform=typeform, mode=mode, cursorPos=cursorPos)
			if cells and (seg_script != primary_script or table != primary_chain):
				if tactile_marker == "dot8_first":
					cells = [cells[0] | BRAILLE_DOT_8] + cells[1:]
				elif tactile_marker == "dot7_first":
					cells = [cells[0] | BRAILLE_DOT_7] + cells[1:]
				elif tactile_marker == "dots78_secondary":
					cells = [cell | BRAILLE_DOTS_7_8 for cell in cells]
			return cells, b2r, r2b, cur
		except Exception:
			return original_translate(active_tables, inbuf, typeform=typeform, mode=mode, cursorPos=cursorPos)

	all_cells: List[int] = []
	all_b2r: List[int] = []
	all_r2b: List[int] = []
	final_cursor_pos: Optional[int] = None
	text_len = len(inbuf)

	prev_table: Optional[List[str]] = None

	for idx, (seg_text, start_idx, end_idx, script) in enumerate(segments):
		table = resolve_segment_table(
			seg_text, start_idx, end_idx, script, active_tables, doc_lang_spans, full_inbuf=inbuf
		)

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
			is_lang_switch = (idx > 0 and (script != segments[idx - 1][3] or (prev_table is not None and table != prev_table)))
			is_secondary = (script != primary_script or table != primary_chain)
			if tactile_marker == "dot8_first" and is_lang_switch:
				cells = [cells[0] | BRAILLE_DOT_8] + cells[1:]
			elif tactile_marker == "dot7_first" and is_lang_switch:
				cells = [cells[0] | BRAILLE_DOT_7] + cells[1:]
			elif tactile_marker == "dots78_secondary" and is_secondary:
				cells = [cell | BRAILLE_DOTS_7_8 for cell in cells]

		prev_table = table

		cell_offset = len(all_cells)
		all_cells.extend(cells)

		# Remap positions for cursor routing keys (cells -> raw characters)
		for cell_idx in b2r:
			all_b2r.append(start_idx + cell_idx)

		# Remap positions for caret / focus cursor (raw characters -> cells)
		for char_idx in r2b:
			all_r2b.append(cell_offset + char_idx)

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
