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


def segment_text(
	text: str,
	enabled_scripts: Optional[Set[str]] = None,
	primary_script: str = "latin",
	default_script: Optional[str] = None,
) -> List[Tuple[str, int, int, str]]:
	"""Partition text into contiguous (slice_text, start_index, end_index, script) segments.

	Guarantees:
	- Every character in text is covered in order without gaps or overlaps.
	- ``''.join(seg[0] for seg in segments) == text``.
	- Sub-microsecond execution when no secondary scripts are present via early regex escape.
	"""
	if not text:
		return []

	if default_script is not None:
		primary_script = default_script

	if enabled_scripts is None:
		enabled_scripts = set(scripts_data.get_all_script_ids())

	# Secondary scripts are any enabled scripts other than the primary script
	secondary_scripts = {s for s in enabled_scripts if s != primary_script}

	# Instant fast-path: If text has no secondary script characters, return as whole segment
	if not has_secondary_scripts(text, secondary_scripts):
		return [(text, 0, len(text), primary_script)]

	scanner = get_scanner_regex(enabled_scripts)

	# Scan all script tokens in a single native C regex pass
	raw_matches = [
		(m.start(), m.end(), m.lastgroup)
		for m in scanner.finditer(text)
		if m.lastgroup in enabled_scripts
	]

	if not raw_matches:
		return [(text, 0, len(text), primary_script)]

	# Pure single-script optimization: If all matches belong to the same script
	first_script = raw_matches[0][2]
	if all(m[2] == first_script for m in raw_matches):
		return [(text, 0, len(text), first_script)]

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

			# Inspect neutral gap for natural punctuation or space boundaries
			for idx, ch in enumerate(gap_text):
				if ch in OPENING_PUNCT:
					split_point = cur_end + idx
					break
				if ch in CLOSING_PUNCT:
					split_point = cur_end + idx + 1
					break
				if ch == " ":
					split_point = cur_end + idx + 1
					break

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
				merged.append((text[cur_seg_start:cur_seg_end], cur_seg_start, cur_seg_end, cur_seg_type))
			cur_seg_start = start
			cur_seg_end = end
			cur_seg_type = s_type

	if cur_seg_end > cur_seg_start:
		merged.append((text[cur_seg_start:cur_seg_end], cur_seg_start, cur_seg_end, cur_seg_type))

	return merged


