import os
from pathlib import Path
from PIL import Image

DATASET = Path("combined_dataset")

# Change this if your classes are different
NUM_CLASSES = 2

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

stats = {
    "valid": 0,
    "segmentation": 0,
    "invalid": 0,
    "missing_image": 0,
    "corrupt_image": 0,
    "missing_label": 0,
}

problems = []


def find_image(label_path):
    stem = label_path.stem
    image_dir = label_path.parent.parent / "images"

    for ext in IMAGE_EXTENSIONS:
        image = image_dir / (stem + ext)
        if image.exists():
            return image

    return None


for split in ["train", "valid", "test"]:

    label_dir = DATASET / split / "labels"
    image_dir = DATASET / split / "images"

    if not label_dir.exists():
        print(f"WARNING: {label_dir} does not exist")
        continue

    print(f"\nChecking {split}...")

    label_files = list(label_dir.glob("*.txt"))

    for label_file in label_files:

        # Check corresponding image
        image_path = find_image(label_file)

        if image_path is None:
            stats["missing_image"] += 1
            problems.append(
                f"MISSING IMAGE: {label_file}"
            )
            continue

        # Check image integrity
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception:
            stats["corrupt_image"] += 1
            problems.append(
                f"CORRUPT IMAGE: {image_path}"
            )
            continue

        # Check label
        try:
            with open(label_file, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception:
            stats["invalid"] += 1
            problems.append(
                f"CANNOT READ LABEL: {label_file}"
            )
            continue

        file_valid = True

        for line_number, line in enumerate(lines, 1):

            parts = line.split()

            # Detection format MUST have exactly 5 values
            if len(parts) != 5:
                stats["segmentation"] += 1
                problems.append(
                    f"NOT DETECTION FORMAT: "
                    f"{label_file}:{line_number} "
                    f"({len(parts)} values)"
                )
                file_valid = False
                continue

            try:
                class_id = int(parts[0])
                coords = [float(x) for x in parts[1:]]
            except ValueError:
                stats["invalid"] += 1
                problems.append(
                    f"INVALID VALUES: "
                    f"{label_file}:{line_number}"
                )
                file_valid = False
                continue

            # Class ID
            if class_id < 0 or class_id >= NUM_CLASSES:
                stats["invalid"] += 1
                problems.append(
                    f"INVALID CLASS ID: "
                    f"{label_file}:{line_number} "
                    f"class={class_id}"
                )
                file_valid = False

            # YOLO coordinates must be between 0 and 1
            for value in coords:
                if value < 0 or value > 1:
                    stats["invalid"] += 1
                    problems.append(
                        f"INVALID COORDINATE: "
                        f"{label_file}:{line_number} "
                        f"value={value}"
                    )
                    file_valid = False

        if file_valid:
            stats["valid"] += 1


print("\n" + "=" * 60)
print("DATASET VALIDATION REPORT")
print("=" * 60)

for key, value in stats.items():
    print(f"{key:20}: {value}")

print("=" * 60)

if problems:
    print("\nPROBLEMS FOUND:\n")

    for problem in problems[:100]:
        print(problem)

    if len(problems) > 100:
        print(
            f"\n...and {len(problems) - 100} more problems."
        )

else:
    print("\n✅ NO PROBLEMS FOUND")