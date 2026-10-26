from auto_language import detect_language


IMAGE = "41keZ6BvtCS._AC_UF1000,1000_QL80_.jpg"


language, score, results = detect_language(IMAGE)


print("\n========== AUTO LANGUAGE RESULT ==========\n")

print(f"Detected language : {language}")
print(f"Best score        : {score:.3f}")

print("\nOCR results from winning language:\n")


for item in results:

    print(f"Text       : {item['original_text']}")
    print(f"Confidence : {item['confidence']:.2f}")
    print(f"Box        : {item['box']}")

    print("--------------------------------------")