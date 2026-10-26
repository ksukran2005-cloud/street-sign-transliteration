import unicodedata

SCRIPT_RANGES = {
    "hi": (0x0900, 0x097F),
    "te": (0x0C00, 0x0C7F),
    "ta": (0x0B80, 0x0BFF),
    "kn": (0x0C80, 0x0CFF),
    "ml": (0x0D00, 0x0D7F),
}

SUPPORTED_LANGUAGES = {"hi", "te", "ta", "kn"}


def script_counts(text: str) -> dict:
    counts = {language: 0 for language in SCRIPT_RANGES}

    for char in text:
        if not unicodedata.category(char).startswith("L"):
            continue

        code = ord(char)

        for language, (start, end) in SCRIPT_RANGES.items():
            if start <= code <= end:
                counts[language] += 1
                break

    return counts


def detect_script(text: str) -> str:
    counts = script_counts(text)

    if not text or max(counts.values(), default=0) == 0:
        return "unknown"

    detected = max(counts, key=counts.get)

    if detected not in SUPPORTED_LANGUAGES:
        return "unsupported"

    return detected


def script_match_score(text: str, expected_language: str) -> float:
    if expected_language not in SUPPORTED_LANGUAGES:
        return 0.0

    counts = script_counts(text)
    total_letters = sum(counts.values())

    if total_letters == 0:
        return 0.0

    if any(
        counts[language] > 0
        for language in counts
        if language not in SUPPORTED_LANGUAGES
    ):
        return 0.0

    return counts[expected_language] / total_letters