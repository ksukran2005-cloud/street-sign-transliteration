import os

os.environ["FLAGS_use_mkldnn"] = "0"

from paddleocr import PaddleOCR

from language_detector import script_match_score


# Only four languages for the application
CANDIDATE_LANGUAGES = [
    "hi",
    "te",
    "ta",
    "kn",
]


def combined_score(ocr_confidence, script_score):

    if script_score < 0.5:
        return 0.0

    return (
        0.7 * ocr_confidence
        + 0.3 * script_score
    )


def detect_language(image_path):

    best_language = None
    best_score = 0.0
    best_results = []

    for language in CANDIDATE_LANGUAGES:
        print(f"Testing language: {language}")
        ocr_language = "ka" if language == "kn" else language
        ocr = PaddleOCR(
            lang=ocr_language,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

        result = ocr.predict(image_path)

        language_results = []

        language_best_score = 0.0

        for res in result:

            texts = res["rec_texts"]
            scores = res["rec_scores"]
            boxes = res["rec_boxes"]

            for text, score, box in zip(
                texts,
                scores,
                boxes
            ):

                confidence = float(score)

                if confidence < 0.5:
                    continue

                script_score = script_match_score(
                    text,
                    language
                )

                score_value = combined_score(
                    confidence,
                    script_score
                )

                language_results.append({
                    "original_text": text,
                    "confidence": confidence,
                    "box": box.tolist(),
                })

                if score_value > language_best_score:

                    language_best_score = score_value

        print(
            f"Best score for {language}: "
            f"{language_best_score:.3f}"
        )

        if language_best_score > best_score:

            best_score = language_best_score

            best_language = language

            best_results = language_results

    return (
        best_language,
        best_score,
        best_results
    )