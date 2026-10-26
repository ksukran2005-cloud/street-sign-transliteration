import cv2

MAX_DIMENSION = 1280


def preprocess_image(image_path, output_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    height, width = image.shape[:2]

    longest_side = max(height, width)

    if longest_side > MAX_DIMENSION:
        scale = MAX_DIMENSION / longest_side

        image = cv2.resize(
            image,
            (
                int(width * scale),
                int(height * scale),
            ),
            interpolation=cv2.INTER_AREA,
        )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(gray)

    success = cv2.imwrite(
        output_path,
        enhanced,
    )

    if not success:
        raise ValueError(
            f"Could not save processed image: {output_path}"
        )

    return output_path