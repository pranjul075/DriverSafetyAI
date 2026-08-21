# src/visualization.py
# ─────────────────────────────────────────────
# Visualization module
#
# Draws all the visual elements on the video frame:
# - Bounding boxes around detected objects
# - Driver ROI rectangle
# - Vehicle motion status
# - Violation status and warnings
# - Confirmation progress bars
# ─────────────────────────────────────────────

import cv2
from src.violation_manager import NORMAL
from config.config import CLASS_PHONE, CLASS_SMOKER, CLASS_SEATBELT

# Colors in BGR format (OpenCV uses BGR, not RGB)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_ORANGE = (0, 165, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (255, 0, 0)

# Bounding box colors per class
CLASS_COLORS = {
    CLASS_PHONE: COLOR_YELLOW,    # Phone = Yellow
    CLASS_SMOKER: COLOR_ORANGE,   # Smoker = Orange
    CLASS_SEATBELT: COLOR_BLUE,   # Seatbelt = Blue
}


def draw_detections(frame, detections):
    """
    Draw bounding boxes and labels for all detections.

    Driver detections (inside ROI) get solid colored boxes.
    Non-driver detections get grey boxes (passenger/background).

    Args:
        frame: OpenCV BGR frame
        detections: list of Detection objects
    """
    for det in detections:
        x1, y1, x2, y2 = det.bbox

        if det.inside_roi:
            # Driver detection — use class color, solid box
            color = CLASS_COLORS.get(det.class_id, COLOR_WHITE)
            thickness = 2
        else:
            # Non-driver detection — grey, thinner box
            color = (128, 128, 128)
            thickness = 1

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

        # Draw label: "Phone 0.87" or "Smoker 0.92"
        label = f"{det.class_name} {det.confidence:.2f}"

        # Draw black background behind text for readability
        (text_w, text_h), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        cv2.rectangle(
            frame,
            (x1, y1 - text_h - 6),
            (x1 + text_w, y1),
            color, -1  # -1 = filled rectangle
        )

        # Draw text
        cv2.putText(
            frame, label,
            (x1, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, COLOR_BLACK, 1
        )

    return frame


def draw_status_panel(frame, motion_status, violation_state,
                      violation_manager):
    """
    Draw the status panel in the top-left corner showing:
    - Vehicle motion status
    - Current violation state
    - Confirmation progress bars

    Args:
        frame: OpenCV BGR frame
        motion_status: string from MotionDetector.get_status_text()
        violation_state: current violation state constant
        violation_manager: ViolationManager instance
    """
    # Semi-transparent background panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (320, 160), COLOR_BLACK, -1)
    # Blend with original frame (0.6 opacity)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # ── Vehicle Motion Status ──
    motion_color = COLOR_GREEN if "MOVING" in motion_status else COLOR_RED
    cv2.putText(
        frame, f"Vehicle: {motion_status}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6, motion_color, 2
    )

    # ── Violation Status ──
    if violation_state == NORMAL:
        status_text = "Driver: NORMAL"
        status_color = COLOR_GREEN
    else:
        status_text = f"WARNING: {violation_state}"
        status_color = COLOR_RED

    cv2.putText(
        frame, status_text,
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6, status_color, 2
    )

    # ── Confirmation Progress Bars ──
    # Shows how close each class is to triggering a violation
    bar_labels = {
        CLASS_PHONE: ("Phone", COLOR_YELLOW),
        CLASS_SMOKER: ("Smoke", COLOR_ORANGE),
        CLASS_SEATBELT: ("Belt", COLOR_BLUE),
    }

    y_pos = 90
    for class_id, (label, color) in bar_labels.items():
        progress = violation_manager.get_confirmation_progress(class_id)

        # Draw label
        cv2.putText(
            frame, f"{label}:",
            (20, y_pos),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45, COLOR_WHITE, 1
        )

        # Draw progress bar background (grey)
        cv2.rectangle(frame, (80, y_pos - 10), (220, y_pos), (50, 50, 50), -1)

        # Draw progress bar fill
        fill_width = int(140 * progress)
        if fill_width > 0:
            cv2.rectangle(
                frame,
                (80, y_pos - 10),
                (80 + fill_width, y_pos),
                color, -1
            )

        # Draw percentage text
        cv2.putText(
            frame, f"{int(progress * 100)}%",
            (225, y_pos),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4, COLOR_WHITE, 1
        )

        y_pos += 22

    return frame


def draw_warning_banner(frame, violation_state):
    """
    Draw a large red warning banner at the bottom
    of the frame when a violation is active.

    Args:
        frame: OpenCV BGR frame
        violation_state: current violation state
    """
    if violation_state == NORMAL:
        return frame

    height, width = frame.shape[:2]

    # Warning messages
    warning_messages = {
        "PHONE_VIOLATION": "⚠ PHONE DETECTED WHILE DRIVING",
        "SMOKING_VIOLATION": "⚠ SMOKING DETECTED WHILE DRIVING",
        "SEATBELT_VIOLATION": "⚠ SEATBELT NOT DETECTED",
        "PHONE_SMOKING_VIOLATION": "⚠ PHONE + SMOKING VIOLATION",
        "PHONE_SEATBELT_VIOLATION": "⚠ PHONE + NO SEATBELT",
        "SMOKING_SEATBELT_VIOLATION": "⚠ SMOKING + NO SEATBELT",
        "ALL_VIOLATION": "⚠ PHONE + SMOKING + NO SEATBELT",
    }

    message = warning_messages.get(violation_state, "⚠ VIOLATION DETECTED")

    # Draw red banner at bottom
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (0, height - 50),
        (width, height),
        COLOR_RED, -1
    )
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    # Draw warning text centered
    (text_w, text_h), _ = cv2.getTextSize(
        message, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2
    )
    text_x = (width - text_w) // 2
    cv2.putText(
        frame, message,
        (text_x, height - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8, COLOR_WHITE, 2
    )

    return frame