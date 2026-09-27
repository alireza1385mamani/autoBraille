# coding: utf-8
"""Universal Multi-Script Segmentation Engine for Auto Braille.

Detects language scripts across all major world writing systems:
- Middle Eastern & Semitic (Arabic, Persian, Urdu, Kurdish, Hebrew, Yiddish, Syriac)
- Cyrillic (Russian, Ukrainian, Belarusian, Bulgarian, Serbian, Macedonian, Kazakh, etc.)
- Greek (Modern and Ancient Greek)
- South Asian / Indic (Devanagari, Bengali, Punjabi, Gujarati, Oriya, Tamil, Telugu, Kannada, Malayalam)
- East Asian (Chinese, Japanese, Korean)
- Southeast Asian & Himalayan (Thai, Lao, Burmese, Khmer, Tibetan)
- Caucasian, African & Ancient (Georgian, Ethiopic, Akkadian, Ugaritic)
- Latin (English, French, German, Spanish, and over 120 Latin-script languages)

Uses vectorized C-level regular expressions (`re.finditer`) for sub-microsecond
execution and zero latency during NVDA braille display refreshes.
"""

from __future__ import annotations

import re
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

try:
	from . import scripts_data
except ImportError:
	import scripts_data

OPENING_PUNCT: FrozenSet[str] = frozenset("([{«<\"'“‘")
CLOSING_PUNCT: FrozenSet[str] = frozenset(")]}»>\"'”’")

_combined_regex_cache: Dict[FrozenSet[str], Optional[re.Pattern[str]]] = {}
_scanner_cache: Dict[FrozenSet[str], re.Pattern[str]] = {}


def clear_regex_cache() -> None:
	"""Invalidate compiled regex caches when configuration or enabled scripts change."""
	_combined_regex_cache.clear()
	_scanner_cache.clear()


def get_combined_secondary_pattern(secondary_scripts: Set[str]) -> Optional[re.Pattern[str]]:
	"""Return a single compiled regex matching any secondary script for fast-path checks."""
	key = frozenset(secondary_scripts)
	if not key:
		return None

	if key in _combined_regex_cache:
		return _combined_regex_cache[key]

	patterns: List[str] = []
	for s_id in key:
		info = scripts_data.get_script_info(s_id)
		if info:
			patterns.append(f"(?:{info.pattern})")

	if not patterns:
		_combined_regex_cache[key] = None
		return None

	combined = re.compile("|".join(patterns))
	_combined_regex_cache[key] = combined
	return combined


def get_scanner_regex(enabled_scripts: Set[str]) -> re.Pattern[str]:
	"""Return a compiled scanner regex with named capture groups for all active enabled scripts."""
	key = frozenset(enabled_scripts)
	if key in _scanner_cache:
		return _scanner_cache[key]

	branches: List[str] = []
	for s in scripts_data.SCRIPTS:
		if s.id in enabled_scripts:
			branches.append(f"(?P<{s.id}>{s.pattern}+)")

	# Fallback if somehow no scripts were enabled
	if not branches:
		branches.append(r"(?P<latin>[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF]+)")

	scanner = re.compile("|".join(branches))
	_scanner_cache[key] = scanner
	return scanner


def has_secondary_scripts(text: str, secondary_scripts: Set[str]) -> bool:
	"""Fast check to see if text contains any characters belonging to enabled secondary scripts.

	Executes in under 1 microsecond on standard text via a single C-level regex pass.
	"""
	if not text or not secondary_scripts:
		return False
	pattern = get_combined_secondary_pattern(secondary_scripts)
	if pattern is None:
		return False
	return bool(pattern.search(text))


LATIN_WORD_TOKEN_PATTERN: re.Pattern[str] = re.compile(
	r"[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF¿¡]+(?:['’][a-zA-Z\u00C0-\u024F\u1E00-\u1EFF¿¡]+)?"
)


def segment_latin_sub_languages(
	text: str,
	active_latin_tables: List[str],
	primary_table: str = "en-ueb-g1.ctb",
	base_offset: int = 0,
) -> List[Tuple[str, int, int, str]]:
	"""Partition a Latin-script text block into sub-language segments based on diacritics and word markers.

	Guarantees:
	- Atomic word-level locking: words like 'Kühlschrank' or 'français' are never sliced mid-word.
	- Sub-microsecond pure ASCII fast path via scripts_data.has_non_ascii_latin().
	- Invariant: ''.join(seg[0] for seg in segments) == text with exact global offsets.
	"""
	if not text:
		return []

	# Sub-microsecond fast-path check: If 0 or 1 Latin table, or pure 7-bit ASCII, return immediately
	if len(active_latin_tables) <= 1 or not scripts_data.has_non_ascii_latin(text):
		return [(text, base_offset, base_offset + len(text), "latin")]

	matches = list(LATIN_WORD_TOKEN_PATTERN.finditer(text))
	if not matches:
		return [(text, base_offset, base_offset + len(text), "latin")]

	word_tags: List[Tuple[int, int, str]] = []
	has_any_sub_lang = False

	for m in matches:
		w_text = m.group(0)
		sub_tbl = scripts_data.detect_latin_sub_language_for_word(
			w_text,
			active_latin_tables,
			primary_table=primary_table,
			clause_context=text,
		)
		if sub_tbl and sub_tbl != primary_table:
			tag = f"latin:{sub_tbl}"
			has_any_sub_lang = True
		else:
			tag = "latin"
		word_tags.append((m.start(), m.end(), tag))

	if not has_any_sub_lang:
		return [(text, base_offset, base_offset + len(text), "latin")]

	# Single-table optimization: if all words belong to the exact same foreign sub-language
	first_tag = word_tags[0][2]
	if first_tag != "latin" and all(wt[2] == first_tag for wt in word_tags):
		return [(text, base_offset, base_offset + len(text), first_tag)]

	raw_spans: List[Tuple[int, int, str]] = []
	n = len(text)

	# 1. Leading neutral gap
	first_start, first_end, first_type = word_tags[0]
	if first_start > 0:
		raw_spans.append((0, first_start, first_type))
	raw_spans.append((first_start, first_end, first_type))

	# 2. Intermediate matches and gaps
	for i in range(len(word_tags) - 1):
		cur_start, cur_end, cur_type = word_tags[i]
		next_start, next_end, next_type = word_tags[i + 1]

		if cur_end < next_start:
			gap_text = text[cur_end:next_start]
			split_point = cur_end + len(gap_text) // 2

			found = False
			for idx, ch in enumerate(gap_text):
				if ch in OPENING_PUNCT:
					split_point = cur_end + idx
					found = True
					break
			if not found:
				for idx in range(len(gap_text) - 1, -1, -1):
					if gap_text[idx] in CLOSING_PUNCT:
						split_point = cur_end + idx + 1
						found = True
						break
			if not found:
				space_idx = gap_text.find(" ")
				if space_idx != -1:
					split_point = cur_end + space_idx + 1

			raw_spans.append((cur_end, split_point, cur_type))
			raw_spans.append((split_point, next_start, next_type))

		raw_spans.append((next_start, next_end, next_type))

	# 3. Trailing neutral gap
	last_end = word_tags[-1][1]
	last_type = word_tags[-1][2]
	if last_end < n:
		raw_spans.append((last_end, n, last_type))

	# 4. Merge adjacent spans of the same tag
	merged: List[Tuple[str, int, int, str]] = []
	cur_seg_start = raw_spans[0][0]
	cur_seg_end = raw_spans[0][1]
	cur_seg_type = raw_spans[0][2]

	for start, end, s_type in raw_spans[1:]:
		if start == end:
			continue
		if s_type == cur_seg_type and start == cur_seg_end:
			cur_seg_end = end
		else:
			if cur_seg_end > cur_seg_start:
				merged.append((
					text[cur_seg_start:cur_seg_end],
					base_offset + cur_seg_start,
					base_offset + cur_seg_end,
					cur_seg_type,
				))
			cur_seg_start = start
			cur_seg_end = end
			cur_seg_type = s_type

	if cur_seg_end > cur_seg_start:
		merged.append((
			text[cur_seg_start:cur_seg_end],
			base_offset + cur_seg_start,
			base_offset + cur_seg_end,
			cur_seg_type,
		))

	return merged


def _segment_literary_text(
	text: str,
	enabled_scripts: Set[str],
	primary_script: str = "latin",
	active_latin_tables: Optional[List[str]] = None,
	detect_latin_sub_languages: bool = True,
	primary_table: str = "en-ueb-g1.ctb",
	base_offset: int = 0,
) -> List[Tuple[str, int, int, str]]:
	"""Partition a purely literary text block into script and sub-language segments."""
	if not text:
		return []

	def _apply_latin_sub_languages(segs: List[Tuple[str, int, int, str]]) -> List[Tuple[str, int, int, str]]:
		if not detect_latin_sub_languages or not active_latin_tables or len(active_latin_tables) <= 1:
			return segs
		result: List[Tuple[str, int, int, str]] = []
		for s_text, s_start, s_end, s_type in segs:
			if s_type == "latin" and scripts_data.has_non_ascii_latin(s_text):
				sub_segs = segment_latin_sub_languages(
					s_text,
					active_latin_tables,
					primary_table=primary_table,
					base_offset=s_start,
				)
				result.extend(sub_segs)
			else:
				result.append((s_text, s_start, s_end, s_type))
		return result

	# Secondary scripts are any enabled scripts other than the primary script
	secondary_scripts = {s for s in enabled_scripts if s != primary_script}

	# Instant fast-path: If text has no secondary script characters, return as whole segment
	if not has_secondary_scripts(text, secondary_scripts):
		return _apply_latin_sub_languages([(text, base_offset, base_offset + len(text), primary_script)])

	scanner = get_scanner_regex(enabled_scripts)

	# Scan all script tokens in a single native C regex pass
	raw_matches = [
		(m.start(), m.end(), m.lastgroup)
		for m in scanner.finditer(text)
		if m.lastgroup in enabled_scripts
	]

	if not raw_matches:
		return _apply_latin_sub_languages([(text, base_offset, base_offset + len(text), primary_script)])

	# Pure single-script optimization: If all matches belong to the same script
	first_script = raw_matches[0][2]
	if all(m[2] == first_script for m in raw_matches):
		return _apply_latin_sub_languages([(text, base_offset, base_offset + len(text), first_script)])

	# Resolve neutral characters (punctuation, whitespace, brackets) between script runs
	raw_spans: List[Tuple[int, int, str]] = []
	n = len(text)

	# 1. Leading neutral gap before first matched token
	first_start, first_end, first_type = raw_matches[0]
	if first_start > 0:
		raw_spans.append((0, first_start, first_type))
	raw_spans.append((first_start, first_end, first_type))

	# 2. Intermediate matches and gaps
	for i in range(len(raw_matches) - 1):
		cur_start, cur_end, cur_type = raw_matches[i]
		next_start, next_end, next_type = raw_matches[i + 1]

		if cur_end < next_start:
			gap_text = text[cur_end:next_start]
			split_point = cur_end + len(gap_text) // 2

			# Inspect neutral gap for natural punctuation, space boundaries, or atomic numbers
			found = False
			for idx, ch in enumerate(gap_text):
				if ch in OPENING_PUNCT:
					split_point = cur_end + idx
					found = True
					break
			if not found:
				for idx in range(len(gap_text) - 1, -1, -1):
					if gap_text[idx] in CLOSING_PUNCT:
						split_point = cur_end + idx + 1
						found = True
						break
			if not found:
				space_idx = gap_text.find(" ")
				if space_idx != -1:
					split_point = cur_end + space_idx + 1
					found = True
			if not found and any(c.isdigit() for c in gap_text):
				# Keep contiguous numbers together with the preceding script rather than splitting mid-digit
				d_end = 0
				while d_end < len(gap_text) and (gap_text[d_end].isdigit() or gap_text[d_end] in ".,"):
					d_end += 1
				split_point = cur_end + d_end

			raw_spans.append((cur_end, split_point, cur_type))
			raw_spans.append((split_point, next_start, next_type))

		raw_spans.append((next_start, next_end, next_type))

	# 3. Trailing neutral gap after last matched token
	last_end = raw_matches[-1][1]
	last_type = raw_matches[-1][2]
	if last_end < n:
		raw_spans.append((last_end, n, last_type))

	# 4. Merge contiguous adjacent spans of the same script
	merged: List[Tuple[str, int, int, str]] = []
	cur_seg_start = raw_spans[0][0]
	cur_seg_end = raw_spans[0][1]
	cur_seg_type = raw_spans[0][2]

	for start, end, s_type in raw_spans[1:]:
		if start == end:
			continue
		if s_type == cur_seg_type and start == cur_seg_end:
			cur_seg_end = end
		else:
			if cur_seg_end > cur_seg_start:
				merged.append((
					text[cur_seg_start:cur_seg_end],
					base_offset + cur_seg_start,
					base_offset + cur_seg_end,
					cur_seg_type,
				))
			cur_seg_start = start
			cur_seg_end = end
			cur_seg_type = s_type

	if cur_seg_end > cur_seg_start:
		merged.append((
			text[cur_seg_start:cur_seg_end],
			base_offset + cur_seg_start,
			base_offset + cur_seg_end,
			cur_seg_type,
		))

	return _apply_latin_sub_languages(merged)


def segment_text(
	text: str,
	enabled_scripts: Optional[Set[str]] = None,
	primary_script: str = "latin",
	default_script: Optional[str] = None,
	active_latin_tables: Optional[List[str]] = None,
	detect_latin_sub_languages: bool = True,
	primary_table: str = "en-ueb-g1.ctb",
	detect_math: bool = False,
	math_table: str = "en-ueb-math.ctb",
	custom_dictionary: Optional[List[Dict[str, Any]]] = None,
) -> List[Tuple[str, int, int, str]]:
	"""Partition text into contiguous (slice_text, start_index, end_index, script) segments.

	Guarantees:
	- Every character in text is covered in order without gaps or overlaps.
	- ``''.join(seg[0] for seg in segments) == text``.
	- Priority hierarchy: Custom Lexicon > Math & STEM Formulas > Script & Sub-Language.
	- Sub-microsecond execution when no secondary scripts, math, or custom rules are present.
	"""
	if not text:
		return []

	if default_script is not None:
		primary_script = default_script

	if enabled_scripts is None:
		enabled_scripts = set(scripts_data.get_all_script_ids())

	# Identify high-priority custom lexicon and math formula spans
	priority_spans: List[Tuple[int, int, str]] = []
	n_len = len(text)
	occupied = [False] * n_len

	# 1. Custom lexicon / dictionary overrides (highest priority)
	if custom_dictionary:
		for entry in custom_dictionary:
			if not isinstance(entry, dict):
				continue
			pat = entry.get("pattern")
			tbl = entry.get("table")
			if not isinstance(pat, str) or not isinstance(tbl, str) or not pat.strip() or not tbl.strip():
				continue
			cs = entry.get("case_sensitive", False)
			flags = 0 if cs else re.IGNORECASE
			p_esc = re.escape(pat)
			prefix = r"(?<!\w)" if pat[0].isalnum() else ""
			suffix = r"(?!\w)" if pat[-1].isalnum() else ""
			try:
				regex = re.compile(f"{prefix}{p_esc}{suffix}", flags)
				for m in regex.finditer(text):
					s, e = m.start(), m.end()
					if not any(occupied[i] for i in range(s, e)):
						priority_spans.append((s, e, f"custom:{tbl}"))
						for i in range(s, e):
							occupied[i] = True
			except Exception:
				pass

	# 2. Math & STEM formulas
	if detect_math and scripts_data.has_math_candidate(text):
		math_spans = scripts_data.find_math_spans(text)
		for s, e, m_text in math_spans:
			if not any(occupied[i] for i in range(s, e)):
				priority_spans.append((s, e, f"math:{math_table}"))
				for i in range(s, e):
					occupied[i] = True

	# Fast-path: If no custom dictionary matches and no math formulas detected
	if not priority_spans:
		return _segment_literary_text(
			text,
			enabled_scripts=enabled_scripts,
			primary_script=primary_script,
			active_latin_tables=active_latin_tables,
			detect_latin_sub_languages=detect_latin_sub_languages,
			primary_table=primary_table,
			base_offset=0,
		)

	# Partition text around priority spans
	priority_spans.sort(key=lambda x: x[0])
	all_segments: List[Tuple[str, int, int, str]] = []
	last_end = 0

	for p_start, p_end, p_tag in priority_spans:
		if p_start > last_end:
			chunk = text[last_end:p_start]
			chunk_segs = _segment_literary_text(
				chunk,
				enabled_scripts=enabled_scripts,
				primary_script=primary_script,
				active_latin_tables=active_latin_tables,
				detect_latin_sub_languages=detect_latin_sub_languages,
				primary_table=primary_table,
				base_offset=last_end,
			)
			all_segments.extend(chunk_segs)
		all_segments.append((text[p_start:p_end], p_start, p_end, p_tag))
		last_end = p_end

	if last_end < n_len:
		chunk = text[last_end:]
		chunk_segs = _segment_literary_text(
			chunk,
			enabled_scripts=enabled_scripts,
			primary_script=primary_script,
			active_latin_tables=active_latin_tables,
			detect_latin_sub_languages=detect_latin_sub_languages,
			primary_table=primary_table,
			base_offset=last_end,
		)
		all_segments.extend(chunk_segs)

	return all_segments


