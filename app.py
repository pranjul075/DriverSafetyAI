# app.py
# ─────────────────────────────────────────────
# DriverSafetyAI — Main Application
#
# This is the entry point of the system.
# It wires together all the modules:
# - YOLO detector
# - Driver ROI
# - Motion detector
# - Violation manager
# - Audio alert
# - Visualization
#
# Usage:
#   python app.py --source 0          (webcam)
#   python app.py --source video.mp4  (video file)
#   python app.py --select-roi        (reselect ROI)
# ─────────────────────────────────────────────

import cv2
import argparse
import sys
from config.config import (
    DEFAULT_SOURCE,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT
)
from src.detector import Detector
from src.roi import select_roi_interactive, load_roi, draw_roi
from src.motion_detector import MotionDetector
from src.violation_manager import ViolationManager, NORMAL
from src.audio_alert import AudioAlert
from src.visualization import (
    draw_detections,
    draw_status_panel,
    draw_warning_banner
)


def parse_args():
    """
    Parse command line arguments.
    This lets you run:
        python app.py --source 0
        python app.py --source driving.mp4
        python app.py --select-roi
    """
    parser = argparse.ArgumentParser(description="DriverSafetyAI")

    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help="Video source: 0 for webcam, or path to video file"
    )

    parser.add_argument(
        "--select-roi",
        action="store_true",
        help="Force re-selection of Driver ROI"
    )

    return parser.parse_args()


def get_roi(source, force_select=False):
    """
    Get the Driver ROI — either load saved one or
    let user select interactively.

    Args:
        source: video source (0 or file path)
        force_select: if True, always show selection window

    Returns:
        (x1, y1, x2, y2) ROI coordinates
    """
    # Try loading a saved ROI first
    if not force_select:
        roi = load_roi()
        if roi is not None:
            print(f"Using saved ROI: {roi}")
            return roi

    # No saved ROI — let user select interactively
    print("No saved ROI found — please select Driver ROI")

    # Convert source to int if it's a webcam number
    try:
        src = int(source)
    except (ValueError, TypeError):
        src = source

    roi = select_roi_interactive(src)

    if roi is None:
        print("ROI selection failed — using full frame")
        return (0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)

    return roi


def open_video_source(source):
    """
    Open the video source (webcam or file).

    Args:
        source: 0 for webcam, or path to video file

    Returns:
        cv2.VideoCapture object
    """
    # Convert to int if webcam
    try:
        src = int(source)
    except (ValueError, TypeError):
        src = source

    cap = cv2.VideoCapture(src)

    if not cap.isOpened():
        print(f"ERROR: Could not open video source: {source}")
        sys.exit(1)

    print(f"Video source opened: {source}")
    print(f"  FPS: {cap.get(cv2.CAP_PROP_FPS):.1f}")
    print(f"  Resolution: "
          f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
          f"{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")

    return cap


def main():
    print("=" * 50)
    print("  DriverSafetyAI — Starting up")
    print("=" * 50)

    # Parse command line arguments
    args = parse_args()

    # ── Initialize all modules ──────────────────
    print("\n[1/5] Loading YOLO model...")
    detector = Detector()

    print("\n[2/5] Setting up Driver ROI...")
    roi = get_roi(args.source, force_select=args.select_roi)

    print("\n[3/5] Initializing motion detector...")
    motion_detector = MotionDetector()

    print("\n[4/5] Initializing violation manager...")
    violation_manager = ViolationManager()

    print("\n[5/5] Initializing audio alert...")
    audio_alert = AudioAlert()

    # ── Open video source ───────────────────────
    print("\nOpening video source...")
    cap = open_video_source(args.source)

    print("\n✅ System ready!")
    print("Press Q to quit")
    print("Press R to reselect ROI")
    print("Press SPACE to pause/resume")
    print("=" * 50)

    paused = False
    frame_count = 0

    # ── Main Loop ───────────────────────────────
    while True:
        # Handle pause
        if paused:
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                paused = False
            elif key == ord('q'):
                break
            continue

        # Read next frame from video source
        ret, frame = cap.read()

        if not ret:
            print("Video ended or frame read failed")
            break

        frame_count += 1

        # Resize frame for consistent display
        frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

        # ── Step 1: Motion Detection ─────────────
        vehicle_moving = motion_detector.update(frame)
        motion_status = motion_detector.get_status_text()

        # ── Step 2: YOLO Detection ───────────────
        # Get ALL detections (driver + passengers)
        all_detections = detector.detect(frame, roi)

        # Filter to ONLY driver detections (inside ROI)
        driver_detections = [d for d in all_detections if d.inside_roi]

        # ── Step 3: Violation Check ──────────────
        violation_state, should_warn = violation_manager.update(
            driver_detections,
            vehicle_moving
        )

        # ── Step 4: Audio Warning ────────────────
        if should_warn:
            audio_alert.play(violation_state)

        # ── Step 5: Draw Everything ──────────────
        # Draw Driver ROI rectangle
        violation_active = violation_state != NORMAL
        frame = draw_roi(frame, roi, violation=violation_active)

        # Draw bounding boxes for all detections
        frame = draw_detections(frame, all_detections)

        # Draw status panel (top left)
        frame = draw_status_panel(
            frame,
            motion_status,
            violation_state,
            violation_manager
        )

        # Draw warning banner (bottom) if violation active
        frame = draw_warning_banner(frame, violation_state)

        # ── Show Frame ───────────────────────────
        cv2.imshow("DriverSafetyAI", frame)

        # ── Keyboard Controls ────────────────────
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            # Q = quit
            print("Quitting...")
            break

        elif key == ord('r'):
            # R = reselect ROI
            print("Reselecting ROI...")
            cap.release()
            roi = get_roi(args.source, force_select=True)
            cap = open_video_source(args.source)
            motion_detector.reset()
            violation_manager.reset()

        elif key == ord(' '):
            # SPACE = pause
            paused = True
            print("Paused — press SPACE to resume")

    # ── Cleanup ──────────────────────────────────
    cap.release()
    cv2.destroyAllWindows()
    print("DriverSafetyAI stopped.")


if __name__ == "__main__":
    main()