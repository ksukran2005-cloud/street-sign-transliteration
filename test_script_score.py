from language_detector import script_match_score


samples = [
    ("అనుమతి లేని", "te"),
    ("అనుమతి లేని", "hi"),
    ("அனுமதி இல்லை", "ta"),
    ("eலலபJD", "ta"),
    ("नमस्ते", "hi"),
]


print("\n========== SCRIPT MATCH TEST ==========\n")

for text, language in samples:

    score = script_match_score(text, language)

    print(f"Text     : {text}")
    print(f"Language : {language}")
    print(f"Score    : {score:.2f}")
    print("--------------------------------------")