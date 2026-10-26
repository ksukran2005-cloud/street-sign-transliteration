from language_detector import detect_script


samples = {
    "hi": "नमस्ते",
    "te": "నమస్కారం",
    "ta": "வணக்கம்",
    "kn": "ನಮಸ್ಕಾರ",
    "ml": "നമസ്കാരം",
    "gu": "નમસ્તે",
    "bn": "নমস্কার",
    "or": "ନମସ୍କାର",
    "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ",
}


print("\n========== LANGUAGE DETECTOR TEST ==========\n")

for expected, text in samples.items():

    detected = detect_script(text)

    print(f"Text      : {text}")
    print(f"Expected  : {expected}")
    print(f"Detected  : {detected}")
    print("------------------------------------------")