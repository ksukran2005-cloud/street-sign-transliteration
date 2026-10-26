import cv2


def preprocess_image(image_path, output_path):
    """
    Preprocess an image before OCR.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Upscale the image
    height, width = image.shape[:2]

    scale = 2

    resized = cv2.resize(
        image,
        (width * scale, height * scale),
        interpolation=cv2.INTER_CUBIC,
    )

    # Convert to grayscale
    gray = cv2.cvtColor(
        resized,
        cv2.COLOR_BGR2GRAY,
    )

    # Improve local contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(gray)

    # Save processed image
    success = cv2.imwrite(
        output_path,
        enhanced,
    )

    if not success:
        raise ValueError(
            f"Could not save processed image: {output_path}"
        )

    return output_path