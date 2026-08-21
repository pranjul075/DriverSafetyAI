from pathlib import Path

ROOT = Path("combined_dataset")

converted_rows = 0
converted_files = 0

def polygon_to_bbox(parts):
    class_id = parts[0]
    coords = list(map(float, parts[1:]))

    xs = coords[0::2]
    ys = coords[1::2]

    xmin = min(xs)
    xmax = max(xs)
    ymin = min(ys)
    ymax = max(ys)

    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2
    width = xmax - xmin
    height = ymax - ymin

    return f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"

for label_file in ROOT.rglob("labels/*.txt"):

    lines = [
        line.strip()
        for line in label_file.read_text().splitlines()
        if line.strip()
    ]

    new_lines = []
    file_changed = False

    for line in lines:
        parts = line.split()

        if len(parts) == 5:
            new_lines.append(line)

        elif len(parts) > 5:
            if (len(parts) - 1) % 2 != 0:
                print(f"SKIPPED INVALID: {label_file}")
                new_lines.append(line)
                continue

            new_lines.append(polygon_to_bbox(parts))
            converted_rows += 1
            file_changed = True

        else:
            print(f"SKIPPED INVALID: {label_file}")
            new_lines.append(line)

    if file_changed:
        label_file.write_text("\n".join(new_lines) + "\n")
        converted_files += 1

print("\n" + "=" * 50)
print("SEGMENTATION CONVERSION COMPLETE")
print("=" * 50)
print("Converted rows :", converted_rows)
print("Converted files:", converted_files)
print("=" * 50)
