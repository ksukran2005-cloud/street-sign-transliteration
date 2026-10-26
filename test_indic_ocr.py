import sys
from huggingface_hub import snapshot_download

repo = snapshot_download(
    "bodhan-ai/indic-ocr",
    local_files_only=True
)

sys.path.insert(0, repo)

from indic_ocr import IndicOCR

parser = IndicOCR.from_pretrained(repo)

image_path = input("Enter the street-sign image path: ").strip().strip('"')

result = parser.parse(image_path)

print("\n========== INDICOCR RESULT ==========\n")
print(result["markdown"])