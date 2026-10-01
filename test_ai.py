from transformers import pipeline

print("Loading CleanSight AI model...")

classifier = pipeline(
    "image-classification",
    model="prithivMLmods/Trash-Net"
)

print("Model loaded successfully!")

# Test image
image_path = "uploads/plastic.jpg"

results = classifier(image_path)

print("\nCleanSight AI Predictions:")

for result in results:
    print(
        result["label"],
        "->",
        round(result["score"] * 100, 2),
        "%"
    )