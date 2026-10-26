from image_preprocessing import preprocess_image


input_image = "street_sign.jpg"
output_image = "preprocessed.jpg"

result = preprocess_image(
    input_image,
    output_image
)

print("Preprocessing successful!")
print("Output:", result)