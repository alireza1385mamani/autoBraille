#!/usr/bin/env python3
# coding: utf-8
"""Extraction tool to generate gettext .pot localization template for Auto Braille.

Extracts all user-facing strings annotated with _("...") across Auto Braille
along with their preceding '# Translators:' guidance comments and manifest metadata.
Outputs to addon/locale/autoBraille.pot compliant with NVDA Add-on Store standards.
"""

from __future__ import annotations

import ast
import configparser
import datetime
import os
import re
import sys
from typing import Dict, List, Tuple


def extract_manifest_strings(manifest_path: str) -> List[Tuple[str, str, str]]:
	"""Extract summary and description from manifest.ini."""
	entries: List[Tuple[str, str, str]] = []
	if not os.path.isfile(manifest_path):
		return entries

	with open(manifest_path, "r", encoding="utf-8-sig") as f:
		content = "[DEFAULT]\n" + f.read()

	cp = configparser.ConfigParser()
	cp.read_string(content)

	summary = cp.get("DEFAULT", "summary", fallback="").strip().strip('"').strip("'")
	if summary:
		entries.append(("manifest.ini:summary", "Add-on summary in manifest", summary))

	desc = cp.get("DEFAULT", "description", fallback="").strip().strip('"""').strip("'''").strip()
	if desc:
		entries.append(("manifest.ini:description", "Long description of the add-on in manifest", desc))

	return entries


def extract_python_strings(py_path: str, rel_path: str) -> List[Tuple[str, str, str]]:
	"""Extract _("...") strings along with their preceding '# Translators:' comments from Python files."""
	entries: List[Tuple[str, str, str]] = []
	with open(py_path, "r", encoding="utf-8") as f:
		lines = f.readlines()

	source = "".join(lines)
	try:
		tree = ast.parse(source, filename=py_path)
	except SyntaxError:
		return entries

	for node in ast.walk(tree):
		if isinstance(node, ast.Call):
			is_gettext = False
			if isinstance(node.func, ast.Name) and node.func.id == "_":
				is_gettext = True

			if is_gettext and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
				msgid = node.args[0].value
				line_no = node.lineno
				loc = f"{rel_path}:{line_no}"

				# Look upward in preceding lines for '# Translators:' comment
				comment = ""
				for offset in range(1, 6):
					scan_idx = line_no - 1 - offset
					if scan_idx < 0:
						break
					l_strip = lines[scan_idx].strip()
					if not l_strip:
						break
					if l_strip.startswith("# Translators:") or l_strip.startswith("# translators:"):
						comment = l_strip.lstrip("#").strip()
						break

				entries.append((loc, comment, msgid))

	return entries


def escape_pot_str(s: str) -> str:
	"""Escape a string for gettext po format."""
	s = s.replace("\\", "\\\\")
	s = s.replace('"', '\\"')
	s = s.replace("\r", "")
	if "\n" in s:
		lines = s.split("\n")
		parts = ['""']
		for idx, line in enumerate(lines):
			suffix = "\\n" if idx < len(lines) - 1 else ""
			parts.append(f'"{line}{suffix}"')
		return "\n".join(parts)
	else:
		return f'"{s}"'


def get_manifest_version(manifest_path: str) -> str:
	"""Read add-on version dynamically from manifest.ini."""
	if not os.path.isfile(manifest_path):
		return "1.0.2"
	with open(manifest_path, "r", encoding="utf-8-sig") as f:
		content = "[DEFAULT]\n" + f.read()
	cp = configparser.ConfigParser()
	cp.read_string(content)
	return cp.get("DEFAULT", "version", fallback="1.0.2").strip().strip('"').strip("'")


def generate_pot() -> str:
	repo_root = os.path.dirname(os.path.abspath(__file__))
	addon_dir = os.path.join(repo_root, "addon")
	manifest_path = os.path.join(addon_dir, "manifest.ini")
	locale_dir = os.path.join(addon_dir, "locale")
	os.makedirs(locale_dir, exist_ok=True)
	pot_path = os.path.join(locale_dir, "autoBraille.pot")
	addon_version = get_manifest_version(manifest_path)

	all_entries: List[Tuple[str, str, str]] = []

	# 1. Manifest strings
	all_entries.extend(extract_manifest_strings(manifest_path))

	# 2. Python strings
	py_files = [
		os.path.join(addon_dir, "globalPlugins", "autoBraille", "__init__.py"),
		os.path.join(addon_dir, "globalPlugins", "autoBraille", "language_dialogs.py"),
		os.path.join(addon_dir, "globalPlugins", "autoBraille", "input_sync.py"),
	]

	for py_path in py_files:
		if os.path.isfile(py_path):
			rel = os.path.relpath(py_path, repo_root).replace("\\", "/")
			all_entries.extend(extract_python_strings(py_path, rel))

	# Deduplicate and group by msgid preserving references and comments
	catalog: Dict[str, Dict[str, Any]] = {}
	for loc, comment, msgid in all_entries:
		if msgid not in catalog:
			catalog[msgid] = {
				"locations": [loc],
				"comments": [comment] if comment else [],
			}
		else:
			if loc not in catalog[msgid]["locations"]:
				catalog[msgid]["locations"].append(loc)
			if comment and comment not in catalog[msgid]["comments"]:
				catalog[msgid]["comments"].append(comment)

	now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M+0000")
	pot_content = [
		'# SOME DESCRIPTIVE TITLE.',
		'# Copyright (C) 2026 Alireza Mamani & Antigravity',
		'# This file is distributed under the same license as the autoBraille package.',
		'# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.',
		'#',
		'#, fuzzy',
		'msgid ""',
		'msgstr ""',
		f'"Project-Id-Version: autoBraille {addon_version}\\n"',
		'"Report-Msgid-Bugs-To: https://github.com/alireza1385mamani/autoBraille/issues\\n"',
		f'"POT-Creation-Date: {now}\\n"',
		'"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"',
		'"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"',
		'"Language-Team: LANGUAGE <LL@li.org>\\n"',
		'"Language: \\n"',
		'"MIME-Version: 1.0\\n"',
		'"Content-Type: text/plain; charset=UTF-8\\n"',
		'"Content-Transfer-Encoding: 8bit\\n"',
		'',
	]

	for msgid, meta in catalog.items():
		for c in meta["comments"]:
			pot_content.append(f"#. {c}")
		for l in meta["locations"]:
			pot_content.append(f"#: {l}")
		pot_content.append(f"msgid {escape_pot_str(msgid)}")
		pot_content.append('msgstr ""')
		pot_content.append('')

	output_text = "\n".join(pot_content)
	with open(pot_path, "w", encoding="utf-8") as f:
		f.write(output_text)

	print(f"Generated {pot_path} with {len(catalog)} translatable messages.")
	return pot_path


if __name__ == "__main__":
	generate_pot()
