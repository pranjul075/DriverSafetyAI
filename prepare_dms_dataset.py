from pathlib import Path
import shutil

# ─── CONFIG ───────────────────────────────────────────────
# Where the downloaded Kaggle dataset lives
SOURCE = Path("/Users/pranjulkatiyar/Downloads/archive")

# Where we want the clean output dataset
OUTPUT = Path("dms_combined")

# Remapping: original class ID → new class ID
# Classes we want to KEEP only
CLASS_REMAP = {
    2: 1,  # Cigarette → smoker (class 1)
    3: 0,  # Phone     → phone  (class 0)
    4: 2,  # Seatbelt  → seatbelt (class 2)
}
# Any class ID NOT in CLASS_REMAP is dropped (Open Eye=0, Closed Eye=1)
# ──────────────────────────────────────────────────────────


def create_folders():
    """Create the output folder structure."""
    for split in ["train", "valid", "test"]:
        (OUTPUT / split / "images").mkdir(parents=True, exist_ok=True)
        (OUTPUT / split / "labels").mkdir(parents=True, exist_ok=True)
    print("✅ Output folders created")


def process_split(split):
    """Process one split (train/valid/test)."""
    image_dir = SOURCE / split / "images"
    label_dir = SOURCE / split / "labels"

    if not image_dir.exists():
        print(f"⚠️  {split}/images not found, skipping")
        return

    images_copied = 0
    labels_written = 0
    lines_kept = 0
    lines_dropped = 0

    for image in image_dir.iterdir():
        # Only process image files
        if image.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
            continue

        # Find the matching label file
        label_file = label_dir / (image.stem + ".txt")

        if not label_file.exists():
            # No label file = no annotations, skip this image
            continue

        # Read and remap the label file
        new_lines = []
        with open(label_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue

                original_class = int(parts[0])

                if original_class in CLASS_REMAP:
                    # Remap the class ID and keep this line
                    parts[0] = str(CLASS_REMAP[original_class])
                    new_lines.append(" ".join(parts))
                    lines_kept += 1
                else:
                    # Drop this line (Open Eye or Closed Eye)
                    lines_dropped += 1

        # Only copy image + write label if we kept at least one line
        # (avoids copying images that only had dropped classes)
        if new_lines:
            shutil.copy2(image, OUTPUT / split / "images" / image.name)
            images_copied += 1

            with open(OUTPUT / split / "labels" / (image.stem + ".txt"), "w") as f:
                f.write("\n".join(new_lines))
            labels_written += 1

    print(f"{split}: {images_copied} images, {labels_written} labels, "
          f"{lines_kept} annotations kept, {lines_dropped} dropped")


def create_yaml():
    """Write the new data.yaml for the remapped dataset."""
    yaml_content = f"""path: {OUTPUT.resolve()}

train: train/images
val: valid/images
test: test/images

nc: 3

names:
  0: phone
  1: smoker
  2: seatbelt
"""
    with open(OUTPUT / "data.yaml", "w") as f:
        f.write(yaml_content)
    print("✅ data.yaml written")


if __name__ == "__main__":
    print("Starting DMS dataset preparation...")
    create_folders()

    for split in ["train", "valid", "test"]:
        process_split(split)

    create_yaml()
    print(f"\n✅ Done! Dataset saved to: {OUTPUT}")
    