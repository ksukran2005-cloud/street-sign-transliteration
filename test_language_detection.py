from auto_language import detect_language

image_path = input("Enter the street-sign image path: ").strip().strip('"')

language, score, results = detect_language(image_path)

print("\n========== DETECTION RESULTS ==========")
print("Detected language:", language)
print("Detection score:", round(score, 3))

print("\n========== EXTRACTED TEXT ==========")

for item in results:
    print("Text:", item["original_text"])
    print("Confidence:", round(item["confidence"], 3))
    print("Box:", item["box"])
    print()