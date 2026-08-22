import streamlit as st
import cv2
import tempfile
import os

from src.detector import Detector
from src.motion_detector import MotionDetector
from src.violation_manager import ViolationManager
from src.audio_alert import AudioAlert



# PAGE CONFIG


st.set_page_config(
    page_title="DriverSafetyAI",
    page_icon="🚗",
    layout="wide"
)



# HEADER


st.title("🚗 DriverSafetyAI")

st.subheader(
    "Real-Time AI Driver Safety & Violation Detection"
)



# LOAD DETECTOR


@st.cache_resource
def load_detector():

    return Detector()



# PROCESS VIDEO


def process_video(video_path):

    detector = load_detector()

    motion_detector = MotionDetector()

    violation_manager = ViolationManager()

    audio_alert = AudioAlert()


    cap = cv2.VideoCapture(
        video_path
    )


    if not cap.isOpened():

        st.error(
            "Could not open video."
        )

        return


    output_placeholder = st.empty()


    while True:

        ret, frame = cap.read()


        if not ret:

            break


        vehicle_moving = (
            motion_detector.update(
                frame
            )
        )


        detections = detector.detect(
            frame
        )



        (
            violation_state,
            should_warn
        ) = violation_manager.update(
            detections,
            vehicle_moving
        )



        if should_warn:

            audio_alert.play(
                violation_state
            )



        for detection in detections:

            x1, y1, x2, y2 = (
                detection.bbox
            )


            label = (
                f"{detection.class_name} "
                f"{detection.confidence:.2f}"
            )


            # Bounding box

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )


            # Label

            cv2.putText(
                frame,
                label,
                (
                    x1,
                    max(
                        y1 - 10,
                        20
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )



        # CONVERT BGR → RGB

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )



        # DISPLAY


        output_placeholder.image(
            frame,
            channels="RGB",
            use_container_width=True
        )



    # CLEANUP


    cap.release()



# SIDEBAR


st.sidebar.header(
    "Input"
)


uploaded_video = st.sidebar.file_uploader(
    "Upload a driving video",
    type=[
        "mp4",
        "avi",
        "mov",
        "mkv"
    ]
)



# VIDEO UPLOAD


if uploaded_video:

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    ) as temp_file:

        temp_file.write(
            uploaded_video.read()
        )

        video_path = temp_file.name


    st.success(
        "Video uploaded successfully."
    )



    # START DETECTION
    

    if st.button(
        "▶ Start Detection"
    ):

        process_video(
            video_path
        )

    if os.path.exists(
        video_path
    ):

        os.remove(
            video_path
        )