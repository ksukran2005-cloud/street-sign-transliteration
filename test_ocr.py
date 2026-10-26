import os

os.environ["FLAGS_use_mkldnn"] = "0"

from paddleocr import PaddleOCR
from transliterate import transliterate


# Create OCR engine
ocr = PaddleOCR(
    lang="te",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)


# Run OCR
result = ocr.predict("preprocessed_telugu.jpg")


# Process OCR result
for res in result:
    data = res

    texts = data["rec_texts"]
    scores = data["rec_scores"]
    boxes = data["rec_boxes"]

    print("\n========== OCR + TRANSLITERATION ==========\n")

    for text, score, box in zip(texts, scores, boxes):

        # Ignore very low-confidence OCR results
        if float(score) < 0.5:
            continue

        roman = transliterate(text, "te")

        print(f"Original       : {text}")
        print(f"Roman          : {roman}")
        print(f"Confidence     : {float(score):.2f}")
        print(f"Bounding Box   : {box.tolist()}")
        print("------------------------------------------")