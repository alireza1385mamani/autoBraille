# coding: utf-8
"""Universal Multi-Script & World Language Registry for Auto Braille.

Defines all global writing systems supported by Liblouis and NVDA:
- Family grouping for organized, accessible configuration
- Precise, disjoint Unicode regex patterns
- Default Liblouis tables verified against NVDA's library
- Table prefixes and keywords for clean dropdown filtering
- Windows LANGID mappings for Perkins braille keyboard auto-switching
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, FrozenSet, List, NamedTuple, Optional, Set, Tuple


class ScriptInfo(NamedTuple):
	id: str
	name: str
	family: str
	family_name: str
	pattern: str
	default_output_table: str
	default_input_table: str
	table_prefixes: Tuple[str, ...]
	keywords: Tuple[str, ...]
	lang_ids: Tuple[int, ...]
	default_enabled: bool = False


FAMILIES: Dict[str, str] = {
	"primary": "Primary / Latin (English & European Languages)",
	"middle_east": "Middle Eastern & Semitic (Persian, Arabic, Hebrew...)",
	"cyrillic": "Cyrillic (Russian, Ukrainian, Bulgarian...)",
	"greek": "Greek (Modern & Ancient)",
	"indic": "South Asian / Indic (Hindi, Tamil, Bengali...)",
	"east_asian": "East Asian (Chinese, Japanese, Korean)",
	"southeast_asian": "Southeast Asian (Thai, Lao, Burmese, Khmer, Tibetan)",
	"caucasian_african": "Caucasian, African & Ancient (Georgian, Ethiopic...)",
}

SCRIPTS: List[ScriptInfo] = [
	# 1. Primary Latin / English
	ScriptInfo(
		id="latin",
		name="English / Latin (English, European & Latin-script languages)",
		family="primary",
		family_name="English & Latin",
		pattern=r"[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF]",
		default_output_table="en-ueb-g1.ctb",
		default_input_table="en-ueb-g1.ctb",
		table_prefixes=("en-", "us-", "fr-", "de-", "es-", "it-", "pt-", "nl-", "sv-", "no-", "da-", "fi-", "pl-", "cs-", "sk-", "hu-", "ro-", "hr-", "sl-", "tr-", "et-", "lv-", "lt-", "vi-", "sw-", "zu-", "xh-", "af-", "ca-", "cy-", "eo-", "ga-"),
		keywords=("english", "unified", "latin"),
		lang_ids=(0x0409, 0x0809, 0x040C, 0x0407, 0x0C0A, 0x0410, 0x0816, 0x0413, 0x041D, 0x0414, 0x0406, 0x040B, 0x0415, 0x0405, 0x041B, 0x040E, 0x0418, 0x041A, 0x0424, 0x041F),
		default_enabled=True,
	),

	# 2. Middle Eastern & Semitic
	ScriptInfo(
		id="arabic_persian",
		name="Arabic / Persian / Urdu / Kurdish",
		family="middle_east",
		family_name="Middle Eastern & Semitic",
		pattern=r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]",
		default_output_table="fa-ir-g1.utb",
		default_input_table="fa-ir-g1.utb",
		table_prefixes=("fa-", "ar-", "ur-", "ckb-", "ks-"),
		keywords=("persian", "arabic", "farsi", "urdu", "kurdish", "kashmiri"),
		lang_ids=(0x0429, 0x0401, 0x0801, 0x0C01, 0x1001, 0x1401, 0x1801, 0x1C01, 0x2001, 0x2401, 0x2801, 0x2C01, 0x3001, 0x3401, 0x3801, 0x3C01, 0x4001, 0x0420, 0x0492, 0x0460),
		default_enabled=True,
	),
	ScriptInfo(
		id="hebrew",
		name="Hebrew & Yiddish",
		family="middle_east",
		family_name="Middle Eastern & Semitic",
		pattern=r"[\u0590-\u05FF\uFB1D-\uFB4F]",
		default_output_table="he-IL.utb",
		default_input_table="he-IL.utb",
		table_prefixes=("he-", "yi.", "hbo"),
		keywords=("hebrew", "yiddish", "israel"),
		lang_ids=(0x040D, 0x043D),
		default_enabled=True,
	),
	ScriptInfo(
		id="syc",
		name="Syriac",
		family="middle_east",
		family_name="Middle Eastern & Semitic",
		pattern=r"[\u0700-\u074F]",
		default_output_table="syc.utb",
		default_input_table="syc.utb",
		table_prefixes=("syc.",),
		keywords=("syriac",),
		lang_ids=(0x045A,),
		default_enabled=False,
	),

	# 3. Cyrillic
	ScriptInfo(
		id="cyrillic",
		name="Cyrillic (Russian, Ukrainian, Belarusian, Bulgarian, Serbian, etc.)",
		family="cyrillic",
		family_name="Cyrillic",
		pattern=r"[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F]",
		default_output_table="ru-litbrl.ctb",
		default_input_table="ru-litbrl.ctb",
		table_prefixes=("ru-", "uk", "bel", "bg", "sr-Cyrl", "mk-", "kk.", "tt.", "ba.", "sah.", "uz-", "mn-MN"),
		keywords=("russian", "ukrainian", "belarusian", "bulgarian", "serbian", "macedonian", "kazakh", "tatar", "bashkir", "yakut", "uzbek", "mongolian"),
		lang_ids=(0x0419, 0x0422, 0x0423, 0x0402, 0x0C1A, 0x042F, 0x043F, 0x0444, 0x046D, 0x0485, 0x0843, 0x0450),
		default_enabled=True,
	),

	# 4. Greek
	ScriptInfo(
		id="greek",
		name="Greek (Modern & Ancient)",
		family="greek",
		family_name="Greek",
		pattern=r"[\u0370-\u03FF\u1F00-\u1FFF]",
		default_output_table="el.ctb",
		default_input_table="el.ctb",
		table_prefixes=("el.", "grc-", "gr-"),
		keywords=("greek", "hellenic"),
		lang_ids=(0x0408,),
		default_enabled=True,
	),

	# 5. South Asian / Indic
	ScriptInfo(
		id="indic_devanagari",
		name="Devanagari (Hindi, Marathi, Nepali, Sanskrit)",
		family="indic",
		family_name="South Asian / Indic",
		pattern=r"[\u0900-\u097F\uA8E0-\uA8FF]",
		default_output_table="hi-in-g1.utb",
		default_input_table="hi-in-g1.utb",
		table_prefixes=("hi-in", "mr-in", "np-in", "sa-in"),
		keywords=("hindi", "marathi", "nepali", "sanskrit"),
		lang_ids=(0x0439, 0x044E, 0x0461, 0x044F),
		default_enabled=True,
	),
	ScriptInfo(
		id="indic_bengali",
		name="Bengali & Assamese",
		family="indic",
		family_name="South Asian / Indic",
		pattern=r"[\u0980-\u09FF]",
		default_output_table="be-in-g1.utb",
		default_input_table="be-in-g1.utb",
		table_prefixes=("be-in", "as-in", "mn-in"),
		keywords=("bengali", "assamese", "manipuri"),
		lang_ids=(0x0445, 0x044D, 0x0458),
		default_enabled=False,
	),
	ScriptInfo(
		id="indic_gurmukhi",
		name="Gurmukhi (Punjabi)",
		family="indic",
		family_name="South Asian / Indic",
		pattern=r"[\u0A00-\u0A7F]",
		default_output_table="pu-in-g1.utb",
		default_input_table="pu-in-g1.utb",
		table_prefixes=("pu-in",),
		keywords=("punjabi", "gurmukhi"),
		lang_ids=(0x0446,),
		default_enabled=False,
	),
	ScriptInfo(
		id="indic_gujarati",
		name="Gujarati",
		family="indic",
		family_name="South Asian / Indic",
		pattern=r"[\u0A80-\u0AFF]",
		default_output_table="gu-in-g1.utb",
		default_input_table="gu-in-g1.utb",
		table_prefixes=("gu-in",),
		keywords=("gujarati",),
		lang_ids=(0x0447,),
		default_enabled=False,
	),
	ScriptInfo(
		id="indic_oriya",
		name="Oriya (Odia)",
		family="indic",
		family_name="South Asian / Indic",
		pattern=r"[\u0B00-\u0B7F]",
		default_output_table="or-in-g1.utb",
		default_input_table="or-in-g1.utb",
		table_prefixes=("or-in",),
		keywords=("oriya", "odia"),
		lang_ids=(0x0448,),
		default_enabled=False,
	),
	ScriptInfo(
		id="indic_tamil",
		name="Tamil",
		family="indic",
		family_name="South Asian / Indic",
		pattern=r"[\u0B80-\u0BFF]",
		default_output_table="ta-ta-g1.ctb",
		default_input_table="ta-ta-g1.ctb",
		table_prefixes=("ta-ta",),
		keywords=("tamil",),
		lang_ids=(0x0449,),
		default_enabled=False,
	),
	ScriptInfo(
		id="indic_telugu",
		name="Telugu",
		family="indic",
		family_name="South Asian / Indic",
		pattern=r"[\u0C00-\u0C7F]",
		default_output_table="te-in-g1.utb",
		default_input_table="te-in-g1.utb",
		table_prefixes=("te-in",),
		keywords=("telugu",),
		lang_ids=(0x044A,),
		default_enabled=False,
	),
	ScriptInfo(
		id="indic_kannada",
		name="Kannada",
		family="indic",
		family_name="South Asian / Indic",
		pattern=r"[\u0C80-\u0CFF]",
		default_output_table="ka-in-g1.utb",
		default_input_table="ka-in-g1.utb",
		table_prefixes=("ka-in",),
		keywords=("kannada",),
		lang_ids=(0x044B,),
		default_enabled=False,
	),
	ScriptInfo(
		id="indic_malayalam",
		name="Malayalam",
		family="indic",
		family_name="South Asian / Indic",
		pattern=r"[\u0D00-\u0D7F]",
		default_output_table="ml-in-g1.utb",
		default_input_table="ml-in-g1.utb",
		table_prefixes=("ml-in",),
		keywords=("malayalam",),
		lang_ids=(0x044C,),
		default_enabled=False,
	),
	ScriptInfo(
		id="indic_sinhala",
		name="Sinhala",
		family="indic",
		family_name="South Asian / Indic",
		pattern=r"[\u0D80-\u0DFF]",
		default_output_table="sin-in-g1.utb",
		default_input_table="sin-in-g1.utb",
		table_prefixes=("sin-", "si-"),
		keywords=("sinhala", "sinhalese"),
		lang_ids=(0x045B,),
		default_enabled=False,
	),

	# 6. East Asian (CJK)
	ScriptInfo(
		id="cjk_chinese",
		name="Chinese (Simplified Mandarin, Taiwan, Cantonese)",
		family="east_asian",
		family_name="East Asian (CJK)",
		pattern=r"[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]",
		default_output_table="zhcn-g1.ctb",
		default_input_table="zhcn-g1.ctb",
		table_prefixes=("zh",),
		keywords=("chinese", "mandarin", "cantonese", "taiwan"),
		lang_ids=(0x0804, 0x0404, 0x0C04, 0x1404, 0x1004),
		default_enabled=False,
	),
	ScriptInfo(
		id="cjk_japanese",
		name="Japanese (Kana & Kanji)",
		family="east_asian",
		family_name="East Asian (CJK)",
		pattern=r"[\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF]",
		default_output_table="ja-kantenji.utb",
		default_input_table="ja-kantenji.utb",
		table_prefixes=("ja-",),
		keywords=("japanese", "kantenji", "kanji"),
		lang_ids=(0x0411,),
		default_enabled=False,
	),
	ScriptInfo(
		id="cjk_korean",
		name="Korean (Hangul)",
		family="east_asian",
		family_name="East Asian (CJK)",
		pattern=r"[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F\uA960-\uA97F\uD7B0-\uD7FF]",
		default_output_table="ko-g1.ctb",
		default_input_table="ko-g1.ctb",
		table_prefixes=("ko-",),
		keywords=("korean", "hangul"),
		lang_ids=(0x0412,),
		default_enabled=False,
	),

	# 7. Southeast Asian & Himalayan
	ScriptInfo(
		id="sea_thai",
		name="Thai",
		family="southeast_asian",
		family_name="Southeast Asian & Himalayan",
		pattern=r"[\u0E00-\u0E7F]",
		default_output_table="th-g1.utb",
		default_input_table="th-g1.utb",
		table_prefixes=("th-",),
		keywords=("thai",),
		lang_ids=(0x041E,),
		default_enabled=False,
	),
	ScriptInfo(
		id="sea_lao",
		name="Lao",
		family="southeast_asian",
		family_name="Southeast Asian & Himalayan",
		pattern=r"[\u0E80-\u0EFF]",
		default_output_table="lo-g1.utb",
		default_input_table="lo-g1.utb",
		table_prefixes=("lo-",),
		keywords=("lao",),
		lang_ids=(0x0454,),
		default_enabled=False,
	),
	ScriptInfo(
		id="sea_burmese",
		name="Burmese (Myanmar)",
		family="southeast_asian",
		family_name="Southeast Asian & Himalayan",
		pattern=r"[\u1000-\u109F\uAA60-\uAA7F]",
		default_output_table="my-g1.utb",
		default_input_table="my-g1.utb",
		table_prefixes=("my-",),
		keywords=("burmese", "myanmar"),
		lang_ids=(0x0455,),
		default_enabled=False,
	),
	ScriptInfo(
		id="sea_khmer",
		name="Khmer (Cambodia)",
		family="southeast_asian",
		family_name="Southeast Asian & Himalayan",
		pattern=r"[\u1780-\u17FF\u19E0-\u19FF]",
		default_output_table="km-g1.utb",
		default_input_table="km-g1.utb",
		table_prefixes=("km-",),
		keywords=("khmer", "cambodia"),
		lang_ids=(0x0453,),
		default_enabled=False,
	),
	ScriptInfo(
		id="sea_tibetan",
		name="Tibetan",
		family="southeast_asian",
		family_name="Southeast Asian & Himalayan",
		pattern=r"[\u0F00-\u0FFF]",
		default_output_table="bo.ctb",
		default_input_table="bo.ctb",
		table_prefixes=("bo.",),
		keywords=("tibetan",),
		lang_ids=(0x0451,),
		default_enabled=False,
	),

	# 8. Caucasian, African & Ancient
	ScriptInfo(
		id="caucasian_georgian",
		name="Georgian",
		family="caucasian_african",
		family_name="Caucasian, African & Ancient",
		pattern=r"[\u10A0-\u10FF\u2D00-\u2D2F]",
		default_output_table="ka.utb",
		default_input_table="ka.utb",
		table_prefixes=("ka.", "ka-", "ka.utb"),
		keywords=("georgian",),
		lang_ids=(0x0437,),
		default_enabled=False,
	),
	ScriptInfo(
		id="caucasian_armenian",
		name="Armenian",
		family="caucasian_african",
		family_name="Caucasian, African & Ancient",
		pattern=r"[\u0530-\u058F\uFB13-\uFB17]",
		default_output_table="hy.ctb",
		default_input_table="hy.ctb",
		table_prefixes=("hy.", "hy-", "arm-"),
		keywords=("armenian",),
		lang_ids=(0x042B,),
		default_enabled=False,
	),
	ScriptInfo(
		id="african_ethiopic",
		name="Ethiopic (Ge'ez, Amharic)",
		family="caucasian_african",
		family_name="Caucasian, African & Ancient",
		pattern=r"[\u1200-\u137F\u1380-\u139F\u2D80-\u2DDF\uAB00-\uAB2F]",
		default_output_table="ethio-g1.ctb",
		default_input_table="ethio-g1.ctb",
		table_prefixes=("ethio-",),
		keywords=("ethiopic", "amharic", "ge'ez"),
		lang_ids=(0x045E,),
		default_enabled=False,
	),
	ScriptInfo(
		id="ancient_cuneiform",
		name="Ancient (Akkadian, Ugaritic)",
		family="caucasian_african",
		family_name="Caucasian, African & Ancient",
		pattern=r"[\U00010380-\U0001039F\U00012000-\U000123FF]",
		default_output_table="akk.utb",
		default_input_table="akk.utb",
		table_prefixes=("akk.", "akk-", "uga."),
		keywords=("akkadian", "ugaritic"),
		lang_ids=(),
		default_enabled=False,
	),
]

SCRIPT_REGISTRY: Dict[str, ScriptInfo] = {s.id: s for s in SCRIPTS}

LANG_ID_TO_SCRIPT: Dict[int, str] = {}
for s in SCRIPTS:
	for lid in s.lang_ids:
		LANG_ID_TO_SCRIPT[lid] = s.id
		# Also map primary language (low 10 bits) if not yet assigned
		primary = lid & 0x03FF
		if primary not in LANG_ID_TO_SCRIPT:
			LANG_ID_TO_SCRIPT[primary] = s.id

LANG_ID_TO_TABLE: Dict[int, str] = {
	# Persian
	0x0429: "fa-ir-g1.utb",
	# Arabic
	0x0401: "ar-ar-g1.utb",
	0x0801: "ar-ar-g1.utb",
	0x0C01: "ar-ar-g1.utb",
	0x1001: "ar-ar-g1.utb",
	0x1401: "ar-ar-g1.utb",
	0x1801: "ar-ar-g1.utb",
	0x1C01: "ar-ar-g1.utb",
	0x2001: "ar-ar-g1.utb",
	0x2401: "ar-ar-g1.utb",
	0x2801: "ar-ar-g1.utb",
	0x2C01: "ar-ar-g1.utb",
	0x3001: "ar-ar-g1.utb",
	0x3401: "ar-ar-g1.utb",
	0x3801: "ar-ar-g1.utb",
	0x3C01: "ar-ar-g1.utb",
	0x4001: "ar-ar-g1.utb",
	# Urdu
	0x0420: "ur-pk-g1.utb",
	# Kurdish
	0x0492: "ckb.ctb",
	# English
	0x0409: "en-ueb-g1.ctb",
	0x0809: "en-ueb-g1.ctb",
	0x0C09: "en-ueb-g1.ctb",
	0x1009: "en-ueb-g1.ctb",
	0x1409: "en-ueb-g1.ctb",
	0x1809: "en-ueb-g1.ctb",
	0x1C09: "en-ueb-g1.ctb",
	0x2009: "en-ueb-g1.ctb",
	# French
	0x040C: "fr-bfu-comp8.ctb",
	0x080C: "fr-bfu-comp8.ctb",
	0x0C0C: "fr-bfu-comp8.ctb",
	0x100C: "fr-bfu-comp8.ctb",
	# German
	0x0407: "de-g1.ctb",
	0x0807: "de-g1.ctb",
	0x0C07: "de-g1.ctb",
	# Spanish
	0x040A: "es-g1.ctb",
	0x080A: "es-g1.ctb",
	0x0C0A: "es-g1.ctb",
	# Italian
	0x0410: "it-it-g1.utb",
	# Portuguese
	0x0816: "pt-pt-g1.utb",
	0x0416: "pt-pt-g1.utb",
	# Russian
	0x0419: "ru-litbrl.ctb",
	# Ukrainian
	0x0422: "uk.utb",
	# Hebrew
	0x040D: "he-IL.utb",
	# Greek
	0x0408: "el.ctb",
	# Hindi
	0x0439: "hi-in-g1.utb",
}
# Map primary language IDs (low 10 bits) for LANG_ID_TO_TABLE as well
for _lid, _tbl in list(LANG_ID_TO_TABLE.items()):
	_prim = _lid & 0x03FF
	if _prim not in LANG_ID_TO_TABLE:
		LANG_ID_TO_TABLE[_prim] = _tbl



def get_scripts_in_family(family_id: str) -> List[ScriptInfo]:
	"""Return all scripts belonging to the specified family."""
	return [s for s in SCRIPTS if s.family == family_id]


def get_script_info(script_id: str) -> Optional[ScriptInfo]:
	"""Retrieve ScriptInfo by script ID."""
	return SCRIPT_REGISTRY.get(script_id)


def get_all_script_ids() -> List[str]:
	"""Return list of all script IDs in order."""
	return [s.id for s in SCRIPTS]


def get_default_enabled_scripts() -> Set[str]:
	"""Return set of script IDs that are enabled by default."""
	return {s.id for s in SCRIPTS if s.default_enabled}


_table_to_script_cache: Dict[str, ScriptInfo] = {}


def resolve_table_to_script(table_name: str) -> ScriptInfo:
	"""Map any Liblouis table file name directly to its corresponding ScriptInfo."""
	if not table_name:
		return SCRIPT_REGISTRY["latin"]

	base = os.path.basename(table_name).lower()
	if base in _table_to_script_cache:
		return _table_to_script_cache[base]

	# 1. Exact default table match
	for s in SCRIPTS:
		if base == s.default_output_table.lower() or base == s.default_input_table.lower():
			_table_to_script_cache[base] = s
			return s

	# 2. Check non-Latin prefixes
	for s in SCRIPTS:
		if s.id != "latin":
			if any(base.startswith(p.lower()) for p in s.table_prefixes):
				_table_to_script_cache[base] = s
				return s

	# 3. Check non-Latin keywords
	for s in SCRIPTS:
		if s.id != "latin":
			if any(k.lower() in base for k in s.keywords):
				_table_to_script_cache[base] = s
				return s

	# 4. Check Latin prefixes or keywords
	latin_info = SCRIPT_REGISTRY["latin"]
	if any(base.startswith(p.lower()) for p in latin_info.table_prefixes) or any(k.lower() in base for k in latin_info.keywords):
		_table_to_script_cache[base] = latin_info
		return latin_info

	# 5. Default fallback to Latin
	_table_to_script_cache[base] = latin_info
	return latin_info


DOC_LANG_MAP: Dict[str, str] = {
	# Arabic / Persian / Urdu
	"fa": "arabic_persian",
	"per": "arabic_persian",
	"fas": "arabic_persian",
	"ar": "arabic_persian",
	"ara": "arabic_persian",
	"ur": "arabic_persian",
	"urd": "arabic_persian",
	"ku": "arabic_persian",
	"ckb": "arabic_persian",
	"sd": "arabic_persian",
	"ps": "arabic_persian",
	# Hebrew
	"he": "hebrew",
	"heb": "hebrew",
	"yi": "hebrew",
	"yid": "hebrew",
	"iw": "hebrew",
	# Syriac
	"syc": "syc",
	"syr": "syc",
	# Cyrillic
	"ru": "cyrillic",
	"rus": "cyrillic",
	"uk": "cyrillic",
	"ukr": "cyrillic",
	"be": "cyrillic",
	"bel": "cyrillic",
	"bg": "cyrillic",
	"bul": "cyrillic",
	"sr": "cyrillic",
	"srp": "cyrillic",
	"mk": "cyrillic",
	"mkd": "cyrillic",
	"kk": "cyrillic",
	"kaz": "cyrillic",
	"tt": "cyrillic",
	"tat": "cyrillic",
	"ky": "cyrillic",
	"kir": "cyrillic",
	"tg": "cyrillic",
	"tgk": "cyrillic",
	"mn": "cyrillic",
	"mon": "cyrillic",
	# Greek
	"el": "greek",
	"ell": "greek",
	"gre": "greek",
	"grc": "greek",
	# Indic
	"hi": "indic_devanagari",
	"hin": "indic_devanagari",
	"mr": "indic_devanagari",
	"mar": "indic_devanagari",
	"ne": "indic_devanagari",
	"nep": "indic_devanagari",
	"sa": "indic_devanagari",
	"san": "indic_devanagari",
	"bn": "indic_bengali",
	"ben": "indic_bengali",
	"as": "indic_bengali",
	"asm": "indic_bengali",
	"pa": "indic_gurmukhi",
	"pan": "indic_gurmukhi",
	"gu": "indic_gujarati",
	"guj": "indic_gujarati",
	"or": "indic_oriya",
	"ori": "indic_oriya",
	"ta": "indic_tamil",
	"tam": "indic_tamil",
	"te": "indic_telugu",
	"tel": "indic_telugu",
	"kn": "indic_kannada",
	"kan": "indic_kannada",
	"ml": "indic_malayalam",
	"mal": "indic_malayalam",
	"si": "indic_sinhala",
	"sin": "indic_sinhala",
	# CJK
	"zh": "cjk_chinese",
	"zho": "cjk_chinese",
	"chi": "cjk_chinese",
	"yue": "cjk_chinese",
	"ja": "cjk_japanese",
	"jpn": "cjk_japanese",
	"ko": "cjk_korean",
	"kor": "cjk_korean",
	# Southeast Asian
	"th": "sea_thai",
	"tha": "sea_thai",
	"lo": "sea_lao",
	"lao": "sea_lao",
	"my": "sea_burmese",
	"mya": "sea_burmese",
	"km": "sea_khmer",
	"khm": "sea_khmer",
	"bo": "sea_tibetan",
	"bod": "sea_tibetan",
	# Caucasian & African
	"ka": "caucasian_georgian",
	"kat": "caucasian_georgian",
	"geo": "caucasian_georgian",
	"hy": "caucasian_armenian",
	"arm": "caucasian_armenian",
	"hye": "caucasian_armenian",
	"am": "african_ethiopic",
	"amh": "african_ethiopic",
	"ti": "african_ethiopic",
	"tir": "african_ethiopic",
	# Latin / European
	"en": "latin",
	"eng": "latin",
	"de": "latin",
	"deu": "latin",
	"ger": "latin",
	"fr": "latin",
	"fra": "latin",
	"fre": "latin",
	"es": "latin",
	"spa": "latin",
	"it": "latin",
	"ita": "latin",
	"pt": "latin",
	"por": "latin",
	"nl": "latin",
	"nld": "latin",
	"dut": "latin",
	"sv": "latin",
	"swe": "latin",
	"no": "latin",
	"nor": "latin",
	"da": "latin",
	"dan": "latin",
	"fi": "latin",
	"fin": "latin",
	"pl": "latin",
	"pol": "latin",
	"cs": "latin",
	"ces": "latin",
	"cze": "latin",
	"tr": "latin",
	"tur": "latin",
}

_compiled_patterns: Dict[str, Any] = {}


def get_script_pattern(script_id: str) -> Optional[Any]:
	"""Get cached compiled regex pattern for a script ID."""
	if script_id not in _compiled_patterns:
		s = SCRIPT_REGISTRY.get(script_id)
		if s:
			_compiled_patterns[script_id] = re.compile(s.pattern)
		else:
			return None
	return _compiled_patterns[script_id]


def resolve_doc_lang_to_script(doc_lang: str) -> Optional[ScriptInfo]:
	"""Resolve BCP-47 / ISO language tag (e.g. 'fa', 'fa-IR', 'en-US') to ScriptInfo."""
	if not doc_lang:
		return None
	clean = doc_lang.strip().lower().replace("_", "-")
	# 1. Exact match
	if clean in DOC_LANG_MAP:
		return SCRIPT_REGISTRY.get(DOC_LANG_MAP[clean])
	# 2. Match primary subtag (e.g. 'fa' from 'fa-ir')
	primary = clean.split("-")[0]
	if primary in DOC_LANG_MAP:
		return SCRIPT_REGISTRY.get(DOC_LANG_MAP[primary])
	return None


def is_script_compatible(text: str, script_id: str) -> bool:
	"""Validate if text is compatible with script_id.
	Returns True if text contains characters matching script_id or contains only neutral characters (whitespace, numbers, punctuation).
	Returns False if text contains letter characters belonging to a conflicting script.
	"""
	if not text:
		return True
	pat = get_script_pattern(script_id)
	if not pat:
		return True
	if pat.search(text):
		return True
	# If text contains no alphabetic characters at all, it's neutral and compatible
	if not any(c.isalpha() for c in text):
		return True
	return False


def get_script_for_char(char: str) -> Optional[ScriptInfo]:
	"""Determine ScriptInfo for a single character."""
	if not char:
		return None
	for s in SCRIPTS:
		pat = get_script_pattern(s.id)
		if pat and pat.search(char):
			return s
	return SCRIPT_REGISTRY.get("latin")


DOC_LANG_TABLE_MAP: Dict[str, str] = {
	# Middle Eastern
	"fa": "fa-ir-g1.utb",
	"per": "fa-ir-g1.utb",
	"fas": "fa-ir-g1.utb",
	"ar": "ar-ar-g1.utb",
	"ara": "ar-ar-g1.utb",
	"ur": "ur-pk-g1.utb",
	"urd": "ur-pk-g1.utb",
	"ckb": "ckb.ctb",
	"ku": "ckb.ctb",
	"he": "he-IL.utb",
	"heb": "he-IL.utb",
	"yi": "yi.utb",
	"yid": "yi.utb",
	"syc": "syc.utb",
	# Cyrillic
	"ru": "ru-litbrl.ctb",
	"rus": "ru-litbrl.ctb",
	"uk": "uk.utb",
	"ukr": "uk.utb",
	"be": "bel.utb",
	"bel": "bel.utb",
	"bg": "bg.ctb",
	"bul": "bg.ctb",
	"sr": "sr-Cyrl.ctb",
	"srp": "sr-Cyrl.ctb",
	"mk": "mk.ctb",
	"mkd": "mk.ctb",
	"kk": "kk.utb",
	"kaz": "kk.utb",
	"tt": "tt.utb",
	# Greek
	"el": "el.ctb",
	"ell": "el.ctb",
	"gre": "el.ctb",
	"grc": "grc-international-common.uti",
	# Latin / European
	"en": "en-ueb-g1.ctb",
	"eng": "en-ueb-g1.ctb",
	"fr": "fr-bfu-comp8.ctb",
	"fra": "fr-bfu-comp8.ctb",
	"fre": "fr-bfu-comp8.ctb",
	"de": "de-g1.ctb",
	"deu": "de-g1.ctb",
	"ger": "de-g1.ctb",
	"es": "es-g1.ctb",
	"spa": "es-g1.ctb",
	"it": "it-it-g1.utb",
	"ita": "it-it-g1.utb",
	"pt": "pt-pt-g1.utb",
	"por": "pt-pt-g1.utb",
	"nl": "nl-NL-g1.ctb",
	"nld": "nl-NL-g1.ctb",
	"sv": "sv-1989.ctb",
	"swe": "sv-1989.ctb",
	"no": "no-no-8dot.ctb",
	"nor": "no-no-8dot.ctb",
	"da": "da-dk-g1.ctb",
	"dan": "da-dk-g1.ctb",
	"fi": "fi.utb",
	"fin": "fi.utb",
	"pl": "pl-pl-comp8.ctb",
	"pol": "pl-pl-comp8.ctb",
	"cs": "cs-g1.ctb",
	"ces": "cs-g1.ctb",
	"sk": "sk-g1.ctb",
	"slk": "sk-g1.ctb",
	"tr": "tr.ctb",
	"tur": "tr.ctb",
	"ro": "ro.ctb",
	"ron": "ro.ctb",
	"hu": "hu-hu-comp8.ctb",
	"hun": "hu-hu-comp8.ctb",
	"hr": "hr-g1.ctb",
	"sl": "sl-g1.ctb",
	# Indic
	"hi": "hi-in-g1.utb",
	"hin": "hi-in-g1.utb",
	"mr": "mr-in-g1.utb",
	"ne": "np-in-g1.utb",
	"sa": "sa-in-g1.utb",
	"bn": "be-in-g1.utb",
	"pa": "pu-in-g1.utb",
	"gu": "gu-in-g1.utb",
	"ta": "ta-ta-g1.ctb",
	"te": "te-in-g1.utb",
	"kn": "ka-in-g1.utb",
	"ml": "ml-in-g1.utb",
	"si": "si-in-g1.utb",
}


def resolve_doc_lang_to_table(doc_lang: str) -> Optional[str]:
	"""Resolve BCP-47 / ISO language tag directly to a concrete braille table filename."""
	if not doc_lang:
		return None
	clean = doc_lang.strip().lower().replace("_", "-")
	if clean in DOC_LANG_TABLE_MAP:
		return DOC_LANG_TABLE_MAP[clean]
	primary = clean.split("-")[0]
	if primary in DOC_LANG_TABLE_MAP:
		return DOC_LANG_TABLE_MAP[primary]
	return None


TABLE_PREFIX_TO_LANG_NAME: Dict[str, str] = {
	"fa": "Persian",
	"ar": "Arabic",
	"ur": "Urdu",
	"ckb": "Kurdish",
	"en": "English (Unified)",
	"us": "English (US)",
	"fr": "French",
	"de": "German",
	"es": "Spanish",
	"it": "Italian",
	"pt": "Portuguese",
	"nl": "Dutch",
	"sv": "Swedish",
	"no": "Norwegian",
	"da": "Danish",
	"fi": "Finnish",
	"pl": "Polish",
	"cs": "Czech",
	"sk": "Slovak",
	"hu": "Hungarian",
	"ro": "Romanian",
	"hr": "Croatian",
	"sl": "Slovenian",
	"tr": "Turkish",
	"ru": "Russian",
	"uk": "Ukrainian",
	"bel": "Belarusian",
	"bg": "Bulgarian",
	"sr": "Serbian",
	"he": "Hebrew",
	"yi": "Yiddish",
	"el": "Greek",
	"hi": "Hindi",
	"mr": "Marathi",
	"bn": "Bengali",
	"ta": "Tamil",
	"te": "Telugu",
	"ka": "Georgian",
	"hy": "Armenian",
	"am": "Amharic",
	"th": "Thai",
	"zh": "Chinese",
	"ja": "Japanese",
	"ko": "Korean",
}


def get_language_name_for_table(table_file: str, display_name: str = "") -> str:
	"""Return a clean human-readable language name for a braille table."""
	if table_file:
		base = os.path.basename(table_file).lower()
		prefix = base.split("-")[0].split(".")[0]
		if prefix in TABLE_PREFIX_TO_LANG_NAME:
			return TABLE_PREFIX_TO_LANG_NAME[prefix]

	if display_name:
		for marker in (" Grade", " Computer", " Literary", " braille", " (", " contracted", " uncontracted"):
			if marker in display_name:
				cand = display_name.split(marker)[0].strip()
				if cand:
					return cand
		return display_name.strip()

	s_info = resolve_table_to_script(table_file)
	return s_info.family_name if s_info else "Braille"


LANGUAGE_STOP_WORDS: Dict[str, FrozenSet[str]] = {
	"fa": frozenset([
		"در", "به", "از", "که", "را", "با", "برای", "این", "آن", "است", "بود", "شد",
		"یک", "های", "کرد", "بر", "تا", "خود", "یا", "هم", "نیز", "اما", "اگر", "وی",
		"ما", "من", "او", "آنها", "شما", "چه", "چون", "بوده", "شده", "می", "نمی"
	]),
	"ar": frozenset([
		"في", "من", "على", "إلى", "عن", "أن", "إن", "هذا", "هذه", "التي", "الذي",
		"الذين", "كان", "كانت", "ما", "لم", "لن", "مع", "كل", "قد", "لا", "أو",
		"ثم", "حيث", "هو", "هي", "هم", "هن", "نحن", "أنا", "أنت", "تلك", "ذلك", "قال"
	]),
	"en": frozenset([
		"the", "and", "is", "in", "it", "you", "that", "he", "was", "for", "on", "are",
		"as", "with", "his", "they", "at", "be", "this", "have", "from", "or", "one",
		"had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your",
		"can", "said", "there", "use", "an", "each", "which", "she", "do", "how", "their"
	]),
	"fr": frozenset([
		"le", "la", "les", "de", "des", "du", "un", "une", "dans", "sur", "pour", "avec",
		"est", "sont", "qui", "que", "ce", "cette", "ces", "en", "par", "au", "aux",
		"pas", "plus", "ne", "se", "il", "elle", "ils", "elles", "mais", "ou", "et", "donc"
	]),
	"de": frozenset([
		"der", "die", "das", "und", "in", "den", "von", "zu", "mit", "sich", "des", "auf",
		"für", "ist", "im", "dem", "nicht", "ein", "eine", "einer", "einem", "einen",
		"als", "auch", "es", "an", "werden", "aus", "er", "hat", "dass", "sie", "nach", "wird"
	]),
	"es": frozenset([
		"de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un",
		"para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero", "sus", "le",
		"ya", "o", "este", "sí", "porque", "esta", "son", "entre", "está", "cuando"
	]),
}


def get_table_lang_code(table_file: str) -> str:
	"""Extract primary language subtag from table filename (e.g. 'fa' from 'fa-ir-g1.utb')."""
	base = os.path.basename(table_file).lower()
	return base.split("-")[0].split(".")[0]


def detect_intra_script_table(text: str, candidate_tables: List[str]) -> Optional[str]:
	"""Detect which table among candidate tables in the same script family should be used.

	Returns the best-matching candidate table filename, or candidate_tables[0] by default.
	Guarantees loanword stability: single loanwords or ambiguous text never cause a table switch.
	Requires at least 2 distinct stop words of the alternate language to switch.
	"""
	if not text or not candidate_tables:
		return candidate_tables[0] if candidate_tables else None
	if len(candidate_tables) == 1:
		return candidate_tables[0]

	words = [w for w in re.findall(r"\w+", text.lower()) if w]
	if not words:
		return candidate_tables[0]

	base_table = candidate_tables[0]
	base_code = get_table_lang_code(base_table)
	base_stop = LANGUAGE_STOP_WORDS.get(base_code, frozenset())

	base_matches = [w for w in words if w in base_stop]
	base_distinct = len(set(base_matches))

	best_table = base_table
	max_distinct = base_distinct
	max_count = len(base_matches)

	for alt_table in candidate_tables[1:]:
		alt_code = get_table_lang_code(alt_table)
		alt_stop = LANGUAGE_STOP_WORDS.get(alt_code)
		if not alt_stop:
			continue
		alt_matches = [w for w in words if w in alt_stop]
		alt_distinct = len(set(alt_matches))
		alt_count = len(alt_matches)

		if alt_distinct >= 2 and alt_distinct > max_distinct and alt_count > max_count:
			best_table = alt_table
			max_distinct = alt_distinct
			max_count = alt_count

	return best_table


GRADE2_COMPANION_MAP: Dict[str, str] = {
	# English UEB
	"en-ueb-g2.ctb": "en-ueb-g1.ctb",
	"en-ueb-chardefs.uti": "en-ueb-g1.ctb",
	"en-us-g2.ctb": "en-us-g1.ctb",
	"en-gb-g2.ctb": "en-gb-g1.ctb",
	# Arabic
	"ar-ar-g2.ctb": "ar-ar-g1.utb",
	# German
	"de-g2.ctb": "de-g1.ctb",
	"de-g2-detailed.ctb": "de-g1.ctb",
	# French
	"fr-bfu-g2.ctb": "fr-bfu-comp8.ctb",
	"fr-g2.ctb": "fr-bfu-comp8.ctb",
	# Spanish
	"es-g2.ctb": "es-g1.ctb",
	# Italian
	"it-it-g2.ctb": "it-it-g1.utb",
	# Portuguese
	"pt-pt-g2.ctb": "pt-pt-g1.utb",
	# Russian
	"ru-g2.ctb": "ru-litbrl.ctb",
}


def is_contracted_table(table_name: str) -> bool:
	"""Check if a Liblouis table file is a Grade 2 contracted table."""
	if not table_name:
		return False
	base = os.path.basename(table_name).lower()
	if base in GRADE2_COMPANION_MAP:
		return True
	return "-g2" in base or "grade2" in base or "contracted" in base


def get_grade1_companion_table(table_name: str) -> Optional[str]:
	"""Get the uncontracted Grade 1 companion table for a contracted Grade 2 table."""
	if not table_name:
		return None
	base = os.path.basename(table_name).lower()
	if base in GRADE2_COMPANION_MAP:
		return GRADE2_COMPANION_MAP[base]
	# Fallback heuristic: replace -g2 with -g1
	if "-g2" in base:
		return base.replace("-g2", "-g1")
	return None


STANDALONE_VALID_WORDS = frozenset({"a", "i", "A", "I"})


def is_single_letter_wordsign_candidate(text: str) -> bool:
	"""Detect if text is an isolated single letter that would accidentally trigger a Grade 2 word-sign.

	In Grade 2 UEB, isolated letters like 'b' (but), 'c' (can), 'x' (it) contract to whole words.
	When surrounded by foreign text or punctuation, these are variables, shortcuts, or options.
	"""
	if not text:
		return False
	# Strip neutral punctuation and whitespace: e.g. "(b)" or "c." -> "b" or "c"
	cleaned = re.sub(r"[^\w]", "", text)
	if len(cleaned) == 1 and cleaned.isalpha():
		return cleaned not in STANDALONE_VALID_WORDS
	return False


def is_technical_identifier(text: str) -> bool:
	"""Detect if text is a programming identifier, variable, URL, or symbol token.

	Technical tokens (e.g. 'file_name', 'user_id', 'CamelCase', 'path/to/file', 'user@domain')
	should not be corrupted by literary contractions.
	"""
	stripped = text.strip()
	if not stripped:
		return False
	# Check for programming symbols: underscores, backslashes, @, $, #, slashes
	if any(sym in stripped for sym in ("_", "\\", "/", "@", "$", "#", "::", "->")):
		return True
	# Check for CamelCase (uppercase letter inside lowercase word, e.g. 'fileName', 'getData')
	words = stripped.split()
	for w in words:
		if len(w) > 2 and any(c.islower() for c in w) and any(c.isupper() for c in w[1:]):
			return True
	return False


