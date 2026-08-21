# src/roi.py
# ─────────────────────────────────────────────
# Driver Region of Interest (ROI) module
# 
# The camera is inside the car, so both the driver
# and passengers are visible. We use a rectangular
# ROI to define where the DRIVER sits in the frame.
# Only detections inside this ROI are treated as
# driver violations.
# ─────────────────────────────────────────────

import cv2
import json
import os

# File where we save the ROI so you don't have to
# re-select it every time the app starts
ROI_SAVE_PATH = "config/roi.json"


def select_roi_interactive(source=0):
    """
    Opens the camera/video and lets you draw a rectangle
    on the frame to define the Driver ROI.
    
    How to use:
    - A window will open showing the camera frame
    - Click and drag to draw a rectangle around the driver area
    - Press ENTER or SPACE to confirm
    - Press C to cancel/redraw
    
    Returns:
        (x1, y1, x2, y2) — the ROI coordinates in pixels
    """
    print("Opening camera to select Driver ROI...")
    print("Draw a rectangle around the DRIVER area, then press ENTER")

    # Open the video source (webcam or video file)
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print("ERROR: Could not open video source")
        return None

    # Read one frame to use as the background for selection
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("ERROR: Could not read frame from video source")
        return None

    # cv2.selectROI opens an interactive window where you draw a box
    # Parameters: window name, image, show crosshair, show from center
    print("\n[ROI Selection Window]")
    print("- Click and drag to draw the driver region")
    print("- Press ENTER or SPACE to confirm")
    print("- Press C to cancel")

    roi = cv2.selectROI(
        "Select Driver ROI — Press ENTER to confirm",
        frame,
        showCrosshair=True,
        fromCenter=False
    )
    cv2.destroyAllWindows()

    # cv2.selectROI returns (x, y, width, height)
    # We convert to (x1, y1, x2, y2) format
    x, y, w, h = roi

    if w == 0 or h == 0:
        print("No ROI selected — using full frame")
        height, width = frame.shape[:2]
        return (0, 0, width, height)

    x1, y1, x2, y2 = x, y, x + w, y + h
    print(f"ROI selected: ({x1}, {y1}, {x2}, {y2})")

    # Save the ROI to a file so we can reload it next time
    save_roi(x1, y1, x2, y2)

    return (x1, y1, x2, y2)


def save_roi(x1, y1, x2, y2):
    """
    Save ROI coordinates to a JSON file.
    This means you only need to select the ROI once —
    next time the app loads it automatically.
    """
    roi_data = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
    os.makedirs("config", exist_ok=True)

    with open(ROI_SAVE_PATH, "w") as f:
        json.dump(roi_data, f)

    print(f"ROI saved to {ROI_SAVE_PATH}")


def load_roi():
    """
    Load a previously saved ROI from the JSON file.
    
    Returns:
        (x1, y1, x2, y2) if a saved ROI exists
        None if no saved ROI found
    """
    if not os.path.exists(ROI_SAVE_PATH):
        return None

    with open(ROI_SAVE_PATH, "r") as f:
        roi_data = json.load(f)

    x1 = roi_data["x1"]
    y1 = roi_data["y1"]
    x2 = roi_data["x2"]
    y2 = roi_data["y2"]

    print(f"ROI loaded from file: ({x1}, {y1}, {x2}, {y2})")
    return (x1, y1, x2, y2)


def is_inside_roi(bbox_center, roi):
    """
    Check whether a detection's bounding-box center
    falls inside the Driver ROI.
    
    This is the core logic that separates driver detections
    from passenger detections.
    
    Args:
        bbox_center: (cx, cy) — center of the YOLO bounding box
        roi: (x1, y1, x2, y2) — the Driver ROI rectangle
    
    Returns:
        True if the center is inside the ROI
        False if outside (ignore this detection)
    
    Example:
        Driver using phone → center inside ROI → True → violation
        Passenger using phone → center outside ROI → False → ignored
    """
    cx, cy = bbox_center
    x1, y1, x2, y2 = roi

    return x1 <= cx <= x2 and y1 <= cy <= y2


def draw_roi(frame, roi, violation=False):
    """
    Draw the Driver ROI rectangle on the video frame.
    
    Color changes based on violation status:
    - Green = normal, no violation
    - Red = violation detected
    
    Args:
        frame: the OpenCV video frame to draw on
        roi: (x1, y1, x2, y2)
        violation: True if a violation is active
    """
    x1, y1, x2, y2 = roi

    # Choose color based on violation status
    # OpenCV uses BGR color format (not RGB)
    color = (0, 0, 255) if violation else (0, 255, 0)  # Red or Green

    # Draw the rectangle (thickness=2 pixels)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    # Add a label above the rectangle
    label = "DRIVER ROI"
    cv2.putText(
        frame, label,
        (x1, y1 - 10),          # position: just above the top-left corner
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,                      # font size
        color,
        2                         # thickness
    )

    return frame