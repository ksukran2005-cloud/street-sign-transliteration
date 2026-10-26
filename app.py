import os
import re
import uuid

os.environ["FLAGS_use_mkldnn"] = "0"

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.middleware.cors import CORSMiddleware

from transliterate import transliterate
from auto_language import detect_language
from image_preprocessing import preprocess_image


app = FastAPI(
    title="Street Sign Transliteration API",
    version="1.0.0",
    description=(
        "OCR, automatic Indian language detection, "
        "and Roman-script transliteration API"
    ),
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Supported Languages
# --------------------------------------------------

LANGUAGES = {
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
}


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Street Sign Transliteration API",
        "pipeline": (
            "Image → Preprocessing → Language Detection "
            "→ OCR → Transliteration"
        ),
        "supported_languages": list(LANGUAGES.keys()),
    }


# --------------------------------------------------
# Process Image
# --------------------------------------------------

@app.post("/process-image")
async def process_image(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select an image to continue.",
        )

    unique_id = uuid.uuid4().hex
    safe_filename = os.path.basename(file.filename)

    original_path = f"temp_{unique_id}_{safe_filename}"
    processed_path = f"processed_{unique_id}.jpg"

    try:
        # ------------------------------------------
        # Read and Save Uploaded Image
        # ------------------------------------------

        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail=(
                    "The selected file is empty. "
                    "Please choose another image."
                ),
            )

        with open(original_path, "wb") as f:
            f.write(contents)

        # ------------------------------------------
        # Image Preprocessing
        # ------------------------------------------

        preprocess_image(
            original_path,
            processed_path,
        )

        if not os.path.exists(processed_path):
            raise HTTPException(
                status_code=400,
                detail=(
                    "We couldn't prepare this image. "
                    "Please try another image."
                ),
            )

        # ------------------------------------------
        # Language Detection and OCR
        # ------------------------------------------

        detected_language, detection_score, ocr_results = (
            detect_language(processed_path)
        )

        if detected_language not in LANGUAGES:
            raise HTTPException(
                status_code=400,
                detail=(
                    "We couldn't identify a supported language. "
                    "Please upload a clear street sign in "
                    "Hindi, Telugu, Tamil, or Kannada."
                ),
            )

        # ------------------------------------------
        # Check OCR Results
        # ------------------------------------------

        if not ocr_results:
            raise HTTPException(
                status_code=400,
                detail=(
                    "We couldn't recognize any text in this image. "
                    "Try a clearer, well-lit street-sign photo."
                ),
            )

        # Remove empty OCR detections and isolated
        # single-character results.
        usable_results = [
            item
            for item in ocr_results
            if len(
                "".join(
                    item["original_text"].split()
                )
            ) >= 2
        ]

        if not usable_results:
            raise HTTPException(
                status_code=400,
                detail=(
                    "The image is too blurry to read reliably. "
                    "Please upload a clearer street-sign photo."
                ),
            )

        ocr_results = usable_results

        # ------------------------------------------
        # Sort OCR Results by Reading Position
        # ------------------------------------------

        sorted_items = sorted(
            ocr_results,
            key=lambda item: (
                (
                    item["box"][1]
                    + item["box"][3]
                ) / 2,
                item["box"][0],
            ),
        )

        # ------------------------------------------
        # Group OCR Text by Line
        # ------------------------------------------

        grouped_lines = []

        for item in sorted_items:
            text = item["original_text"].strip()
            box = item["box"]

            if not text:
                continue

            center_y = (
                box[1] + box[3]
            ) / 2

            item_height = max(
                1,
                box[3] - box[1],
            )

            matched_line = None

            for line in grouped_lines:
                line_height = max(
                    entry["box"][3] - entry["box"][1]
                    for entry in line["items"]
                )

                vertical_tolerance = max(
                    15,
                    max(item_height, line_height) * 0.5,
                )

                if abs(
                    center_y - line["center_y"]
                ) <= vertical_tolerance:
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
                    (
                        entry["box"][1]
                        + entry["box"][3]
                    ) / 2
                    for entry in matched_line["items"]
                ) / len(matched_line["items"])

        grouped_lines.sort(
            key=lambda line: line["center_y"]
        )

        # ------------------------------------------
        # Combine Lines and Transliterate
        # ------------------------------------------

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

            # Remove trailing hyphens and dash characters.
            text = re.sub(
                r"[-‐-‒–—]+$",
                "",
                text,
            ).strip()

            if not text:
                continue

            # --------------------------------------
            # Transliteration
            # --------------------------------------

            roman = transliterate(
                text,
                detected_language,
            )

            roman = re.sub(
                r"[-‐-‒–—]+$",
                "",
                roman,
            ).strip()

            if not roman:
                continue

            # --------------------------------------
            # Average OCR Confidence
            # --------------------------------------

            confidence = sum(
                float(item["confidence"])
                for item in line_items
            ) / len(line_items)

            # --------------------------------------
            # Combined Bounding Box
            # --------------------------------------

            box = [
                min(
                    item["box"][0]
                    for item in line_items
                ),
                min(
                    item["box"][1]
                    for item in line_items
                ),
                max(
                    item["box"][2]
                    for item in line_items
                ),
                max(
                    item["box"][3]
                    for item in line_items
                ),
            ]

            # --------------------------------------
            # Debug Output
            # --------------------------------------

            print(f"DEBUG ORIGINAL TEXT: {text!r}")
            print(f"DEBUG ROMAN TEXT: {roman!r}")

            # --------------------------------------
            # Store Result
            # --------------------------------------

            results.append({
                "original_text": text,
                "transliterated_text": roman,
                "confidence": round(confidence, 2),
                "box": box,
            })

        # ------------------------------------------
        # Final Quality Check
        # ------------------------------------------

        if not results:
            raise HTTPException(
                status_code=400,
                detail=(
                    "We couldn't extract readable text. "
                    "Please try a clearer street-sign image."
                ),
            )

        # ------------------------------------------
        # API Response
        # ------------------------------------------

        return {
            "filename": file.filename,
            "detected_language": detected_language,
            "detection_score": round(
                float(detection_score),
                3,
            ),
            "results": results,
        }

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                "We couldn't read the text in this image. "
                "Please upload a clearer street-sign image."
            ),
        )

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Image processing error: {exc}")

        raise HTTPException(
            status_code=500,
            detail=(
                "Something went wrong while processing the image. "
                "Please try again with another image."
            ),
        )

    finally:
        # ------------------------------------------
        # Delete Temporary Files
        # ------------------------------------------

        for path in (
            original_path,
            processed_path,
        ):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError as exc:
                print(
                    f"Warning: Could not delete {path}: {exc}"
                )