from pathlib import Path
import shutil

#This set  Dataset locations
PHONE_DATASET = Path("Mobile Phone Detection.v1i.yolov11")
SMOKING_DATASET = Path("cigarette smokers.v4-smoker4.yolov11")

# Output dataset location
OUTPUT = Path("combined_dataset")

# in this we create the necessary folder structure for the combined dataset. It creates separate directories for training, validation, and testing splits, each containing subdirectories for images and labels. The use of `mkdir` with `parents=True` ensures that any missing parent directories are also created, and `exist_ok=True` prevents errors if the directories already exist.
def create_folders():
    for split in ["train", "valid", "test"]:
        (OUTPUT / split / "images").mkdir(parents=True, exist_ok=True)
        (OUTPUT / split / "labels").mkdir(parents=True, exist_ok=True)


def process_phone_dataset():
    print("Processing phone dataset...")

    for split in ["train", "valid", "test"]:
        image_dir = PHONE_DATASET / split / "images"
        label_dir = PHONE_DATASET / split / "labels"

        if not image_dir.exists():
            continue

        for image in image_dir.iterdir():

            if image.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
                continue

            # Add phone prefix to avoid duplicate filenames
            new_image_name = "phone_" + image.name
            new_label_name = "phone_" + image.stem + ".txt"

            shutil.copy2(
                image,
                OUTPUT / split / "images" / new_image_name
            )

            label_file = label_dir / (image.stem + ".txt")

            if label_file.exists():
                new_lines = []

                with open(label_file, "r") as f:
                    for line in f:
                        parts = line.strip().split()

                        if not parts:
                            continue

                        class_id = parts[0]

                        # Phone dataset  class 1 = phone
                        # Combined dataset class 0 = phone
                        if class_id == "1":
                            parts[0] = "0"
                        else:
                            print(
                                f"WARNING: Unexpected phone class "
                                f"{class_id} in {label_file}"
                            )

                        new_lines.append(" ".join(parts))

                with open(
                    OUTPUT / split / "labels" / new_label_name,
                    "w"
                ) as f:
                    f.write("\n".join(new_lines))

# it processes the smoking dataset in a similar manner to the phone dataset. It iterates through the train, validation, and test splits, copying images and modifying label files to ensure that class IDs are consistent with the combined dataset's labeling scheme. Specifically, it changes the class ID for smokers from "0" in the original smoking dataset to "1" in the combined dataset.
def process_smoking_dataset():
    print("Processing smoking dataset...")

    for split in ["train", "valid", "test"]:
        image_dir = SMOKING_DATASET / split / "images"
        label_dir = SMOKING_DATASET / split / "labels"

        if not image_dir.exists():
            continue

        for image in image_dir.iterdir():

            if image.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
                continue

            # Add smoker names like prefix to avoid duplicate filenames
            new_image_name = "smoker_" + image.name
            new_label_name = "smoker_" + image.stem + ".txt"
            # it copies the image file from the original smoking dataset to the combined dataset, renaming it with a "smoker_" prefix to avoid filename conflicts.
            shutil.copy2(
                image,
                OUTPUT / split / "images" / new_image_name
            )

            label_file = label_dir / (image.stem + ".txt")
              # if the corresponding label file exists, it reads the label file, modifies the class ID from "0" (smoker in the original dataset) to "1" (smoker in the combined dataset), and writes the modified labels to a new file in the combined dataset's labels directory.
            if label_file.exists():
                new_lines = []

                with open(label_file, "r") as f:
                    for line in f:
                        parts = line.strip().split()

                        if not parts:
                            continue

                        class_id = parts[0]

                        # Smoking dataset:
                        # class 0 = smoker
                        # Combined dataset:
                        # class 1 = smoker
                        if class_id == "0":
                            parts[0] = "1"
                        else:
                            print(
                                f"WARNING: Unexpected smoking class "
                                f"{class_id} in {label_file}"
                            )

                        new_lines.append(" ".join(parts))

                with open(
                    OUTPUT / split / "labels" / new_label_name,
                    "w"
                ) as f:
                    f.write("\n".join(new_lines))

# it creates a YAML configuration file named "data.yaml" in the combined dataset directory. This YAML file contains information about the dataset, including the paths to the training, validation, and test image directories, the number of classes (nc), and the class names (phone and smoker). This configuration file is typically used for training machine learning models with frameworks like YOLO.
def create_yaml():
    yaml_content = """path: combined_dataset

train: train/images
val: valid/images
test: test/images

nc: 2

names:
  0: phone
  1: smoker
"""

    with open(OUTPUT / "data.yaml", "w") as f:
        f.write(yaml_content)


if __name__ == "__main__":
    create_folders()
    process_phone_dataset()
    process_smoking_dataset()
    create_yaml()

    print("\n✅ Dataset combination completed!")
    print(f"Combined dataset: {OUTPUT}")