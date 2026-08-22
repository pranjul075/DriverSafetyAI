# src/detector.py
# ─────────────────────────────────────────────
# DriverSafetyAI — YOLO Detection
#
# Detects:
#   Class 0 → Phone
#   Class 1 → Smoker
#   Class 2 → Seatbelt
#
# Driver ROI has been removed.
# ─────────────────────────────────────────────

from ultralytics import YOLO

from config.config import (
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    CLASS_NAMES
)


class Detection:
    """
    Represents one YOLO detection.
    """

    def __init__(self, class_id, confidence, bbox, center):

        self.class_id = class_id

        self.confidence = confidence

        # Bounding box:
        # (x1, y1, x2, y2)
        self.bbox = bbox

        # Center:
        # (cx, cy)
        self.center = center

        # Human-readable class name
        self.class_name = CLASS_NAMES.get(
            class_id,
            "unknown"
        )

    def __repr__(self):

        return (
            f"Detection("
            f"{self.class_name}, "
            f"conf={self.confidence:.2f})"
        )


class Detector:
    """
    YOLO detector.
    """

    def __init__(self):

        print(
            f"Loading YOLO model from: "
            f"{MODEL_PATH}"
        )

        self.model = YOLO(MODEL_PATH)

        print("Model loaded successfully!")

        print(
            f"Classes: {self.model.names}"
        )

        print(
            f"Confidence threshold: "
            f"{CONFIDENCE_THRESHOLD}"
        )

    def detect(self, frame):
        """
        Run YOLO detection on one frame.

        Returns:
            List of Detection objects.
        """

        detections = []

        results = self.model(
            frame,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False,persist=True
        )

        for result in results:

            boxes = result.boxes

            if boxes is None:
                continue

            for box in boxes:

                confidence = float(
                    box.conf[0]
                )

                class_id = int(
                    box.cls[0]
                )

                # Ignore classes that are
                # not part of our project.
                if class_id not in CLASS_NAMES:
                    continue

                # Bounding box
                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                bbox = (
                    x1,
                    y1,
                    x2,
                    y2
                )

                # Bounding box center
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                center = (
                    cx,
                    cy
                )

                detection = Detection(
                    class_id=class_id,
                    confidence=confidence,
                    bbox=bbox,
                    center=center
                )

                detections.append(
                    detection
                )

        return detections