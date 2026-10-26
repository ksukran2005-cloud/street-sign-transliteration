def combined_score(ocr_confidence: float, script_score: float) -> float:

    # Reject results that don't have enough
    # characters from the expected script.
    if script_score < 0.5:
        return 0.0

    return (
        0.7 * ocr_confidence
        + 0.3 * script_score
    )


samples = [
    ("Telugu correct", 0.94, 1.00),
    ("Tamil garbage", 0.56, 0.50),
    ("Hindi correct", 0.88, 1.00),
    ("Wrong script", 0.90, 0.00),
]


print("\n========== COMBINED SCORE TEST ==========\n")

for name, confidence, script in samples:

    score = combined_score(confidence, script)

    print(f"Case           : {name}")
    print(f"OCR confidence : {confidence:.2f}")
    print(f"Script score   : {script:.2f}")
    print(f"Combined score : {score:.3f}")
    print("-----------------------------------------")