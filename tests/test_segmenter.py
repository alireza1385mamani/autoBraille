import re
from typing import List, Tuple

PERSIAN_ARABIC_PATTERN = re.compile(
	r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
)
LATIN_PATTERN = re.compile(r"[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF]")
OPENING_PUNCT = "([{«<\"'“‘"
CLOSING_PUNCT = ")]}»>\"'”’"

def has_persian_script(text: str) -> bool:
	return bool(PERSIAN_ARABIC_PATTERN.search(text))

def has_latin_script(text: str) -> bool:
	return bool(LATIN_PATTERN.search(text))

def get_char_script(ch: str) -> str:
	if PERSIAN_ARABIC_PATTERN.match(ch):
		return "persian"
	if LATIN_PATTERN.match(ch):
		return "latin"
	return "neutral"

def segment_text(text: str, default_script: str = "latin") -> List[Tuple[str, int, int, str]]:
	if not text:
		return []
	if not has_persian_script(text):
		return [(text, 0, len(text), "latin")]
	if not has_latin_script(text):
		return [(text, 0, len(text), "persian")]

	n = len(text)
	raw_labels = [get_char_script(ch) for ch in text]
	resolved = list(raw_labels)

	for i in range(n):
		if raw_labels[i] == "neutral" and text[i] in OPENING_PUNCT:
			for j in range(i + 1, min(i + 30, n)):
				if raw_labels[j] != "neutral":
					resolved[i] = raw_labels[j]
					break

	current_script = default_script
	for label in raw_labels:
		if label != "neutral":
			current_script = label
			break

	for i in range(n):
		if resolved[i] == "neutral":
			resolved[i] = current_script
		else:
			current_script = resolved[i]

	for i in range(n - 1, -1, -1):
		if raw_labels[i] == "neutral" and text[i] in CLOSING_PUNCT:
			for j in range(i - 1, max(i - 30, -1), -1):
				if raw_labels[j] != "neutral":
					resolved[i] = raw_labels[j]
					break

	segments: List[Tuple[str, int, int, str]] = []
	seg_start = 0
	seg_script = resolved[0]

	for i in range(1, n):
		if resolved[i] != seg_script:
			segments.append((text[seg_start:i], seg_start, i, seg_script))
			seg_start = i
			seg_script = resolved[i]

	segments.append((text[seg_start:n], seg_start, n, seg_script))
	return segments

# Test cases
test_cases = [
    "Hello world",
    "سلام دنیا",
    "Hello سلام world",
    "کتاب (book) شماره ۱",
    "Testing 123 and ۴۵۶ فارسی",
    "(سلام) and (hello)",
]

print("Running segmentation tests:")
for text in test_cases:
    segs = segment_text(text)
    reconstructed = "".join(s[0] for s in segs)
    assert reconstructed == text, f"Reconstruction failed: {reconstructed!r} != {text!r}"
    print(f"\nOriginal: {text}")
    for seg_text, start, end, script in segs:
        print(f"  [{script:7s}] [{start}:{end}] -> {seg_text!r}")

print("\nALL SEGMENTATION TESTS PASSED SUCCESSFULLY!")
