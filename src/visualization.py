# src/visualization.py
# ─────────────────────────────────────────────
# DriverSafetyAI — Visualization
# ─────────────────────────────────────────────

import cv2

from config.config import (
    CLASS_PHONE,
    CLASS_SMOKER,
    CLASS_SEATBELT
)

from src.violation_manager import (
    NORMAL,
    PHONE_VIOLATION,
    SMOKING_VIOLATION,
    SEATBELT_VIOLATION,
    PHONE_SMOKING_VIOLATION,
    PHONE_SEATBELT_VIOLATION,
    SMOKING_SEATBELT_VIOLATION,
    ALL_VIOLATION
)


# ─────────────────────────────────────────────
# DETECTION BOXES
# ─────────────────────────────────────────────

def draw_detections(
    frame,
    detections
):

    for det in detections:

        x1, y1, x2, y2 = det.bbox

        confidence = det.confidence

        label = (
            f"{det.class_name} "
            f"{confidence:.2f}"
        )

        # Default box color
        color = (
            0,
            255,
            0
        )

        # Smoking detection
        if det.class_id == CLASS_SMOKER:

            color = (
                0,
                0,
                255
            )

        # Phone detection
        elif det.class_id == CLASS_PHONE:

            color = (
                255,
                0,
                0
            )

        # Seatbelt detection
        elif det.class_id == CLASS_SEATBELT:

            color = (
                0,
                255,
                255
            )

        # Bounding box
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        # Text background
        text_size = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            2
        )

        text_width = (
            text_size[0][0]
        )

        text_height = (
            text_size[0][1]
        )

        cv2.rectangle(
            frame,
            (
                x1,
                max(
                    0,
                    y1 - text_height - 10
                )
            ),
            (
                x1 + text_width + 10,
                y1
            ),
            color,
            -1
        )

        # Label
        cv2.putText(
            frame,
            label,
            (
                x1 + 5,
                y1 - 5
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    return frame


# ─────────────────────────────────────────────
# STATUS PANEL
# ─────────────────────────────────────────────

def draw_status_panel(
    frame,
    motion_status,
    violation_state,
    violation_manager
):

    # Panel
    cv2.rectangle(
        frame,
        (10, 10),
        (370, 150),
        (0, 0, 0),
        -1
    )

    # Motion
    cv2.putText(
        frame,
        f"Motion: {motion_status}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    # Violation
    cv2.putText(
        frame,
        f"Status: {violation_state}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

    # Confirmation progress
    progress_phone = (
        violation_manager
        .get_confirmation_progress(
            CLASS_PHONE
        )
    )

    progress_smoke = (
        violation_manager
        .get_confirmation_progress(
            CLASS_SMOKER
        )
    )

    progress_belt = (
        violation_manager
        .get_confirmation_progress(
            CLASS_SEATBELT
        )
    )

    cv2.putText(
        frame,
        f"Phone: {progress_phone * 100:.0f}%",
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )

    cv2.putText(
        frame,
        f"Smoke: {progress_smoke * 100:.0f}%",
        (140, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )

    cv2.putText(
        frame,
        f"Belt: {progress_belt * 100:.0f}%",
        (260, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )

    return frame


# ─────────────────────────────────────────────
# WARNING BANNER
# ─────────────────────────────────────────────

def draw_warning_banner(
    frame,
    violation_state
):

    if violation_state == NORMAL:

        return frame

    messages = {

        PHONE_VIOLATION:
            "WARNING: PHONE DETECTED",

        SMOKING_VIOLATION:
            "WARNING: SMOKING DETECTED",

        SEATBELT_VIOLATION:
            "WARNING: SEATBELT NOT DETECTED",

        PHONE_SMOKING_VIOLATION:
            "WARNING: PHONE + SMOKING",

        PHONE_SEATBELT_VIOLATION:
            "WARNING: PHONE + NO SEATBELT",

        SMOKING_SEATBELT_VIOLATION:
            "WARNING: SMOKING + NO SEATBELT",

        ALL_VIOLATION:
            "WARNING: MULTIPLE VIOLATIONS"
    }

    message = messages.get(
        violation_state,
        "WARNING: VIOLATION"
    )

    height, width = frame.shape[:2]

    banner_height = 60

    # Warning banner
    cv2.rectangle(
        frame,
        (0, height - banner_height),
        (width, height),
        (0, 0, 255),
        -1
    )

    # Text
    text_size = cv2.getTextSize(
        message,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        2
    )

    text_width = (
        text_size[0][0]
    )

    text_x = (
        width - text_width
    ) // 2

    cv2.putText(
        frame,
        message,
        (
            text_x,
            height - 20
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    return frame