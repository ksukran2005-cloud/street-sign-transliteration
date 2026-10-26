from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="hi",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

image_path = input("Enter the street-sign image path: ").strip().strip('"')

results = ocr.predict(image_path)

print("\n========== OCR RESULTS ==========\n")

for page in results:
    data = page.json
    if callable(data):
        data = data()

    if isinstance(data, dict):
        res = data.get("res", data)
        texts = res.get("rec_texts", [])
        scores = res.get("rec_scores", [])

        for i, text in enumerate(texts):
            score = scores[i] if i < len(scores) else 0
            print(f"Text: {text} | Confidence: {score:.3f}")
