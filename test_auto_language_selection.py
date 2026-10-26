import os

os.environ["FLAGS_use_mkldnn"] = "0"

from paddleocr import PaddleOCR
from language_detector import script_match_score


IMAGE = "41keZ6BvtCS._AC_UF1000,1000_QL80_.jpg"

# Languages we have actually tested with PaddleOCR
CANDIDATE_LANGUAGES = ["hi", "te", "ta"]


def combined_score(ocr_confidence, script_score):

    if script_score < 0.5:
        return 0.0

    return (
        0.7 * ocr_confidence
        + 0.3 * script_score
    )


best_language = None
best_score = 0.0


print("\n========== REAL AUTO LANGUAGE TEST ==========\n")


for language in CANDIDATE_LANGUAGES:

    print("\n======================================")
    print(f"Testing OCR language: {language}")
    print("======================================")

    ocr = PaddleOCR(
        lang=language,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    result = ocr.predict(IMAGE)

    language_best_score = 0.0

    for res in result:

        texts = res["rec_texts"]
        scores = res["rec_scores"]

        for text, score in zip(texts, scores):

            confidence = float(score)

            if confidence < 0.5:
                continue

            script_score = script_match_score(
                text,
                language
            )

            combined = combined_score(
                confidence,
                script_score
            )

            print(f"Text           : {text}")
            print(f"OCR confidence : {confidence:.2f}")
            print(f"Script score   : {script_score:.2f}")
            print(f"Combined score : {combined:.3f}")
            print("--------------------------------------")

            if combined > language_best_score:
                language_best_score = combined

    print(
        f"Best score for {language}: "
        f"{language_best_score:.3f}"
    )

    if language_best_score > best_score:
        best_score = language_best_score
        best_language = language


print("\n======================================")
print("FINAL LANGUAGE SELECTION")
print("======================================")

print(f"Detected language : {best_language}")
print(f"Best score        : {best_score:.3f}")

print("======================================")