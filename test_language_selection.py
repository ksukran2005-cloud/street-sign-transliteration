def combined_score(ocr_confidence: float, script_score: float) -> float:

    if script_score < 0.5:
        return 0.0

    return (
        0.7 * ocr_confidence
        + 0.3 * script_score
    )


def select_language(candidates):

    best_language = None
    best_score = 0.0

    for language, confidence, script_score in candidates:

        score = combined_score(
            confidence,
            script_score
        )

        print(
            f"{language}: "
            f"confidence={confidence:.2f}, "
            f"script={script_score:.2f}, "
            f"combined={score:.3f}"
        )

        if score > best_score:
            best_score = score
            best_language = language

    return best_language, best_score


# Simulated OCR results
# These represent what we observed from the Telugu image.

candidates = [
    ("hi", 0.00, 0.00),
    ("te", 0.94, 1.00),
    ("ta", 0.56, 0.50),
]


print("\n========== LANGUAGE SELECTION TEST ==========\n")

language, score = select_language(candidates)

print("\n---------------------------------------------")
print(f"Detected Language : {language}")
print(f"Best Score        : {score:.3f}")
print("---------------------------------------------")