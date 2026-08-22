from ultralytics import YOLO

model = YOLO("yolo11n.pt")

model.train(
    data="dms_combined/data.yaml",
    epochs=100,
    imgsz=640,
    batch=16,
    device=0,
    project="runs/detect",
    name="driver_safety",
    patience=20
)