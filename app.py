import os
import re
import uuid
import logging
import threading

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from transliterate import transliterate
from auto_language import detect_language
from image_preprocessing import preprocess_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_UPLOAD_SIZE = 5 * 1024 * 1024

LANGUAGES = {
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
}

processing_lock = threading.Lock()

app = FastAPI(
    title="Street Sign Transliteration API",
    version="1.1.0",
    description="OCR, language detection, and Roman-script transliteration API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Street Sign Transliteration API",
        "supported_languages": LANGUAGES,
        "maximum_upload_size_mb": 5,
    }


@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select an image.",
        )

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/bmp",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Upload a JPEG, PNG, WEBP, or BMP image.",
        )

    unique_id = uuid.uuid4().hex
    original_path = f"temp_{unique_id}.img"
    processed_path = f"processed_{unique_id}.jpg"

    try:
        contents = await file.read(MAX_UPLOAD_SIZE + 1)

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Image size must not exceed 5 MB.",
            )

        with open(original_path, "wb") as image_file:
            image_file.write(contents)

        del contents

        with processing_lock:
            preprocess_image(original_path, processed_path)

            if not os.path.exists(processed_path):
                raise HTTPException(
                    status_code=400,
                    detail="Unable to prepare the image.",
                )

            detected_language, detection_score, ocr_results = (
                detect_language(processed_path)
            )

            if detected_language not in LANGUAGES:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "No supported language detected. Upload a clear "
                        "Hindi, Telugu, Tamil, or Kannada street sign."
                    ),
                )

            usable_results = [
                item
                for item in ocr_results
                if len("".join(item["original_text"].split())) >= 2
            ]

            if not usable_results:
                raise HTTPException(
                    status_code=400,
                    detail="No readable text found. Try a clearer image.",
                )

            sorted_items = sorted(
                usable_results,
                key=lambda item: (
                    (item["box"][1] + item["box"][3]) / 2,
                    item["box"][0],
                ),
            )

            grouped_lines = []

            for item in sorted_items:
                text = item["original_text"].strip()
                box = item["box"]

                if not text:
                    continue

                center_y = (box[1] + box[3]) / 2
                item_height = max(1, box[3] - box[1])
                matched_line = None

                for line in grouped_lines:
                    line_height = max(
                        entry["box"][3] - entry["box"][1]
                        for entry in line["items"]
                    )

                    tolerance = max(
                        15,
                        max(item_height, line_height) * 0.5,
                    )

                    if abs(center_y - line["center_y"]) <= tolerance:
                        matched_line = line
                        break

                if matched_line is None:
                    grouped_lines.append({
                        "center_y": center_y,
                        "items": [item],
                    })
                else:
                    matched_line["items"].append(item)
                    matched_line["center_y"] = sum(
                        (entry["box"][1] + entry["box"][3]) / 2
                        for entry in matched_line["items"]
                    ) / len(matched_line["items"])

            grouped_lines.sort(key=lambda line: line["center_y"])
            results = []

            for line in grouped_lines:
                line_items = sorted(
                    line["items"],
                    key=lambda item: item["box"][0],
                )

                text = " ".join(
                    item["original_text"].strip()
                    for item in line_items
                    if item["original_text"].strip()
                )

                text = re.sub(r"[-‐-‒–—]+$", "", text).strip()

                if not text:
                    continue

                roman = transliterate(text, detected_language)
                roman = re.sub(r"[-‐-‒–—]+$", "", roman).strip()

                if not roman:
                    continue

                confidence = sum(
                    float(item["confidence"])
                    for item in line_items
                ) / len(line_items)

                box = [
                    min(item["box"][0] for item in line_items),
                    min(item["box"][1] for item in line_items),
                    max(item["box"][2] for item in line_items),
                    max(item["box"][3] for item in line_items),
                ]

                results.append({
                    "original_text": text,
                    "transliterated_text": roman,
                    "confidence": round(confidence, 2),
                    "box": box,
                })

            if not results:
                raise HTTPException(
                    status_code=400,
                    detail="No readable text could be transliterated.",
                )

            return {
                "filename": os.path.basename(file.filename),
                "detected_language": detected_language,
                "detection_score": round(float(detection_score), 3),
                "results": results,
            }

    except HTTPException:
        raise

    except ValueError:
        logger.exception("Image validation or preprocessing failed")
        raise HTTPException(
            status_code=400,
            detail="Unable to read the image. Please try another image.",
        )

    except Exception:
        logger.exception("Image processing failed")
        raise HTTPException(
            status_code=500,
            detail="Image processing failed. Please try again.",
        )

    finally:
        await file.close()

        for path in (original_path, processed_path):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                logger.warning("Could not remove temporary file: %s", path)
