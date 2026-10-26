from transliterate import transliterate

tests = [
    ("te", "నమస్కారం ఎలా ఉన్నారు"),
    ("hi", "नमस्ते आप कैसे हैं"),
    ("ta", "வணக்கம் எப்படி இருக்கிறீர்கள்"),
    ("kn", "ನಮಸ್ಕಾರ ಹೇಗಿದ್ದೀರಿ"),
]

for language, text in tests:
    print(f"\n[{language}] {text}")
    try:
        print(" ->", transliterate(text, language))
    except Exception as exc:
        print("ERROR:", exc)