import os
from collections import Counter

def count_classes(labels_dir):
    counter = Counter()
    for fname in os.listdir(labels_dir):
        if fname.endswith(".txt"):
            with open(os.path.join(labels_dir, fname), "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        class_id = int(parts[0])
                        counter[class_id] += 1
    return counter

for split in ["train", "valid", "test"]:
    labels_path = os.path.join("dms_combined", split, "labels")  # ← only this changed
    counts = count_classes(labels_path)
    print(f"{split}: {dict(counts)}")