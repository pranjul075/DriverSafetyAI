# src/detector.py
# ─────────────────────────────────────────────
# YOLO Detection module
#
# This module loads your trained best.pt model
# and runs it on every video frame to detect:
# - Phone (class 0)
# - Smoker (class 1)
# - Seatbelt (class 2)
#
# It also calculates the bounding box center
# and checks if it falls inside the Driver ROI
# ─────────────────────────────────────────────

from ultralytics import YOLO
import cv2
from config.config import (
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    CLASS_PHONE,
    CLASS_SMOKER,
    CLASS_SEATBELT,
    CLASS_NAMES
)
from src.roi import is_inside_roi


class Detection:
    """
    Represents a single YOLO detection result.
    Stores all the information about one detected object.
    """
    def __init__(self, class_id, confidence, bbox, center, inside_roi):
        # Which class was detected (0=phone, 1=smoker, 2=seatbelt)
        self.class_id = class_id

        # How confident YOLO is (0.0 to 1.0)
        self.confidence = confidence

        # Bounding box (x1, y1, x2, y2) in pixels
        self.bbox = bbox

        # Center point of the bounding box (cx, cy)
        self.center = center

        # Whether this detection is inside the Driver ROI
        self.inside_roi = inside_roi

        # Human readable class name
        self.class_name = CLASS_NAMES.get(class_id, "unknown")

    def __repr__(self):
        return (f"Detection({self.class_name}, "
                f"conf={self.confidence:.2f}, "
                f"inside_roi={self.inside_roi})")


class Detector:
    """
    Wraps the YOLO model and runs detection on frames.
    """

    def __init__(self):
        print(f"Loading YOLO model from: {MODEL_PATH}")
        self.model = YOLO(MODEL_PATH)
        print("Model loaded successfully!")
        print(f"Classes: {self.model.names}")

    def detect(self, frame, roi):
        """
        Run YOLO detection on a single frame.

        For each detected object:
        1. Check confidence threshold
        2. Calculate bounding box center
        3. Check if center is inside Driver ROI
        4. Return list of Detection objects

        Args:
            frame: OpenCV BGR frame
            roi: (x1, y1, x2, y2) Driver ROI

        Returns:
            List of Detection objects
        """
        detections = []

        # Run YOLO on the frame
        # verbose=False suppresses per-frame console output
        results = self.model(frame, verbose=False)

        # results is a list — we only process the first item
        # since we're running on one frame at a time
        for result in results:
            boxes = result.boxes

            if boxes is None:
                continue

            for box in boxes:
                # Get confidence score
                confidence = float(box.conf[0])

                # Skip detections below confidence threshold
                if confidence < CONFIDENCE_THRESHOLD:
                    continue

                # Get class ID
                class_id = int(box.cls[0])

                # Skip classes we don't care about
                if class_id not in CLASS_NAMES:
                    continue

                # Get bounding box coordinates (x1, y1, x2, y2)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                bbox = (x1, y1, x2, y2)

                # Calculate the CENTER of the bounding box
                # This is what we compare against the ROI
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                center = (cx, cy)

                # Check if center is inside Driver ROI
                inside = is_inside_roi(center, roi)

                # Create a Detection object and add to list
                detection = Detection(
                    class_id=class_id,
                    confidence=confidence,
                    bbox=bbox,
                    center=center,
                    inside_roi=inside
                )
                detections.append(detection)

        return detections

    def get_driver_detections(self, frame, roi):
        """
        Returns ONLY detections inside the Driver ROI.
        Passenger detections are filtered out here.

        Args:
            frame: OpenCV BGR frame
            roi: (x1, y1, x2, y2)

        Returns:
            List of Detection objects inside ROI only
        """
        all_detections = self.detect(frame, roi)
        driver_detections = [d for d in all_detections if d.inside_roi]
        return driver_detections