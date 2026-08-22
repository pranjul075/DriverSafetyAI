
import cv2
import argparse
import sys

from config.config import (
    DEFAULT_SOURCE,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT
)

from src.detector import Detector

from src.motion_detector import (
    MotionDetector
)

from src.violation_manager import (
    ViolationManager,
    NORMAL
)

from src.audio_alert import (
    AudioAlert
)

from src.visualization import (
    draw_detections,
    draw_status_panel,
    draw_warning_banner
)

# ARGUMENTS

def parse_args():

    parser = argparse.ArgumentParser(
        description="DriverSafetyAI"
    )

    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help=(
            "Video source: "
            "0 for webcam, "
            "or path to video"
        )
    )

    return parser.parse_args()

# VIDEO SOURCE

def open_video_source(source):

    # Convert webcam number from string to int
    try:
        src = int(source)

    except (
        ValueError,
        TypeError
    ):
        src = source

    cap = cv2.VideoCapture(src)

    if not cap.isOpened():

        print(
            f"ERROR: Could not open "
            f"video source: {source}"
        )

        sys.exit(1)

    print(
        f"Video source opened: {source}"
    )

    print(
        f"  FPS: "
        f"{cap.get(cv2.CAP_PROP_FPS):.1f}"
    )

    print(
        "  Resolution: "
        f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}"
        "x"
        f"{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}"
    )

    return cap

# MAIN

def main():

    print("=" * 55)

    print(
        "  DriverSafetyAI — Starting up"
    )

    print("=" * 55)

    # Parse arguments


    args = parse_args()

   
    # 1. YOLO
   

    print(
        "\n[1/4] Loading YOLO model..."
    )

    detector = Detector()


    # 2. Motion detector
   

    print(
        "\n[2/4] Initializing motion detector..."
    )

    motion_detector = MotionDetector()

    # 3. Violation manager
  

    print(
        "\n[3/4] Initializing violation manager..."
    )

    violation_manager = ViolationManager()



    print(
        "\n[4/4] Initializing audio alert..."
    )

    audio_alert = AudioAlert()


    print(
        "\nOpening video source..."
    )

    cap = open_video_source(
        args.source
    )

    print("\n" + "=" * 55)

    print(
        "✅ System ready!"
    )

    print(
        "Press Q to quit"
    )

    print(
        "Press SPACE to pause/resume"
    )

    print("=" * 55)

    paused = False

    frame_count = 0



    while True:



        if paused:

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord(" "):

                paused = False

                print(
                    "Resumed"
                )

            elif key == ord("q"):

                print(
                    "Quitting..."
                )

                break

            continue



        ret, frame = cap.read()

        if not ret:

            print(
                "Video ended or "
                "frame read failed"
            )

            break

        frame_count += 1


        # RESIZE


        frame = cv2.resize(
            frame,
            (
                DISPLAY_WIDTH,
                DISPLAY_HEIGHT
            )
        )


        # STEP 1
        # MOTION DETECTION


        vehicle_moving = (
            motion_detector.update(
                frame
            )
        )

        motion_status = (
            motion_detector
            .get_status_text()
        )


        # STEP 2
        # YOLO DETECTION


        detections = (
            detector.detect(frame)
        )

        # Since ROI has been removed,
        # ALL valid detections are used.
        driver_detections = detections


        # STEP 3
        # VIOLATION MANAGER


        (
            violation_state,
            should_warn
        ) = violation_manager.update(
            driver_detections,
            vehicle_moving
        )


        # STEP 4
        # AUDIO WARNING


        if should_warn:

            audio_alert.play(
                violation_state
            )


        # STEP 5
        # DRAW DETECTIONS


        frame = draw_detections(
            frame,
            detections
        )


        # STATUS PANEL


        frame = draw_status_panel(
            frame,
            motion_status,
            violation_state,
            violation_manager
        )


        # WARNING BANNER


        frame = draw_warning_banner(
            frame,
            violation_state
        )

        
        # DISPLAY
        

        cv2.imshow(
            "DriverSafetyAI",
            frame
        )


        # KEYBOARD


        key = (
            cv2.waitKey(1)
            & 0xFF
        )

        # Q → quit
        if key == ord("q"):

            print(
                "Quitting..."
            )

            break

        # SPACE → pause
        elif key == ord(" "):

            paused = True

            print(
                "Paused — "
                "press SPACE to resume"
            )


    # CLEANUP


    cap.release()

    cv2.destroyAllWindows()

    print(
        "DriverSafetyAI stopped."
    )



# ENTRY POINT


if __name__ == "__main__":

    main()