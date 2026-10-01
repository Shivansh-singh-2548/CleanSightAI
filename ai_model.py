from transformers import pipeline


# Load AI model once
classifier = pipeline(
    "image-classification",
    model="prithivMLmods/Trash-Net"
)


def analyze_waste(image_path):

    results = classifier(image_path)

    return results