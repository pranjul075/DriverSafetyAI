from ultralytics import YOLO  # type: ignore[import-not-found]

# Load a pre-trained YOLO model
model = YOLO("yolo11n.pt")

# Train the model
model.train(
    data="combined_dataset/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16
)