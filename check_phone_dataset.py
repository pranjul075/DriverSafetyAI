from pathlib import Path

PHONE_DATASET = Path("Mobile Phone Detection.v1i.yolov11")

for split in ["train", "valid", "test"]:
    image_dir = PHONE_DATASET / split / "images"
    label_dir = PHONE_DATASET / split / "labels"

    print(f"\n--- {split} ---")
    print("image_dir exists:", image_dir.exists())
    print("label_dir exists:", label_dir.exists())

    if image_dir.exists():
        images = list(image_dir.iterdir())
        print("num images:", len(images))
        if images:
            sample_img = images[0]
            print("sample image name:", sample_img.name)
            expected_label = label_dir / (sample_img.stem + ".txt")
            print("expected label path:", expected_label)
            print("expected label exists:", expected_label.exists())

    if label_dir.exists():
        labels = list(label_dir.iterdir())
        print("num label files:", len(labels))
        if labels:
            print("sample label filename:", labels[0].name)
            with open(labels[0], "r") as f:
                print("sample label content:", f.read().strip())