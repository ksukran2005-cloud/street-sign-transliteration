import os
import gc

os.environ["FLAGS_use_mkldnn"] = "0"

from paddleocr import PaddleOCR
from language_detector import (
    script_match_score,
    script_counts,
    SUPPORTED_LANGUAGES,
)

CANDIDATE_LANGUAGES = ["hi", "te", "ta", "kn"]

MIN_OCR_CONFIDENCE = 0.50
MIN_SCRIPT_MATCH = 0.80
MIN_DETECTION_SCORE = 0.60

_current_language = None
_current_ocr = None


def get_ocr(language):
    global _current_language, _current_ocr

    if language not in CANDIDATE_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")

    if _current_language != language or _current_ocr is None:
        _current_ocr = None
        _current_language = None
        gc.collect()

        ocr_language = "ka" if language == "kn" else language

        _current_ocr = PaddleOCR(
            lang=ocr_language,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

        _current_language = language

    return _current_ocr


def combined_score(ocr_confidence, script_score):
    if script_score < MIN_SCRIPT_MATCH:
        return 0.0

    return 0.7 * ocr_confidence + 0.3 * script_score


def detect_language(image_path):
    best_language = None
    best_score = 0.0
    best_results = []

    for language in CANDIDATE_LANGUAGES:
        print(f"Testing language: {language}")

        ocr = get_ocr(language)
        result = ocr.predict(image_path)

        language_results = []
        language_best_score = 0.0

        for res in result:
            data = res.json

            if callable(data):
                data = data()

            if isinstance(data, dict):
                data = data.get("res", data)

            texts = data.get("rec_texts", [])
            scores = data.get("rec_scores", [])
            boxes = data.get("rec_boxes", [])

            for text, score, box in zip(texts, scores, boxes):
                text = str(text).strip()
                confidence = float(score)

                if confidence < MIN_OCR_CONFIDENCE or not text:
                    continue

                counts = script_counts(text)

                supported_letters = sum(
                    counts[lang]
                    for lang in SUPPORTED_LANGUAGES
                )

                unsupported_letters = sum(
                    count
                    for lang, count in counts.items()
                    if lang not in SUPPORTED_LANGUAGES
                )

                if unsupported_letters > 0 or supported_letters == 0:
                    continue

                script_score = script_match_score(text, language)

                score_value = combined_score(
                    confidence,
                    script_score,
                )

                if score_value == 0.0:
                    continue

                language_results.append({
                    "original_text": text,
                    "confidence": confidence,
                    "box": (
                        box.tolist()
                        if hasattr(box, "tolist")
                        else box
                    ),
                })

                language_best_score = max(
                    language_best_score,
                    score_value,
                )

        print(
            f"Best score for {language}: "
            f"{language_best_score:.3f}"
        )

        if language_best_score > best_score:
            best_score = language_best_score
            best_language = language
            best_results = language_results

    if (
        best_language not in SUPPORTED_LANGUAGES
        or best_score < MIN_DETECTION_SCORE
        or not best_results
    ):
        return None, 0.0, []

    return best_language, best_score, best_results
