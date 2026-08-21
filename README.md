DriverSafetyAI

Real-Time AI Driver Safety & Violation Detection System

DriverSafetyAI is an AI-powered real-time driver monitoring system that uses YOLO object detection, computer vision, temporal violation confirmation, vehicle-motion detection, and audio alerts to identify unsafe driving behaviors.

The system supports real-time webcam and video-file input and can detect smoking, mobile phone usage, and seatbelt violations.

⸻

✨ Features

*  Mobile Phone Detection
*  Smoking Detection
*  Seatbelt Detection
*  Real-Time Webcam Detection
*  Video File Support
*  YOLO-based Object Detection
*  Temporal Violation Confirmation
*  Vehicle Motion Detection
*  Real-Time Audio Warnings
*  Configurable Confidence Threshold
*  Warning Cooldown System
*  Live Detection Visualization
*  Modular Python Architecture

⸻

 How It Works

Webcam / Video
      ↓
OpenCV Frame Capture
      ↓
YOLO Object Detection
      ↓
Confidence Filtering
      ↓
Driver Detection Analysis
      ↓
Vehicle Motion Detection
      ↓
Temporal Violation Confirmation
      ↓
Violation State Detection
      ↓
 ┌───────────────┬────────────────┐
 │               │                │
 ▼               ▼                ▼
Visualization   Audio Alert    Status

The system does not immediately trigger an alarm from a single-frame prediction. A detected violation must remain present for the configured confirmation period before it is considered a confirmed violation.

This helps reduce false alarms caused by temporary or incorrect detections.

⸻

 Detected Violations

The system supports individual and combined violation states:

NORMAL
PHONE_VIOLATION
SMOKING_VIOLATION
SEATBELT_VIOLATION
PHONE_SMOKING_VIOLATION
PHONE_SEATBELT_VIOLATION
SMOKING_SEATBELT_VIOLATION
ALL_VIOLATION

⸻

🔊 Audio Alert System

DriverSafetyAI uses Pygame for audio warnings.

Example alerts include:

Phone detected while driving!
Smoking detected while driving!
Seatbelt not detected!
Phone AND smoking detected!

Audio playback runs independently from the main video-processing loop so that warning sounds do not unnecessarily block the real-time camera feed.

⸻

🛡️ False Positive Reduction

Real-world object detection can produce false positives. DriverSafetyAI therefore combines YOLO predictions with application-level decision logic.

For example:

Object detected
      ↓
Confidence check
      ↓
Detection persists
      ↓
Confirmation timer
      ↓
Violation confirmed
      ↓
Audio warning

The system also uses a configurable warning cooldown to prevent repeated audio alerts from becoming excessive.

For difficult false positives, such as a pen being classified as smoking, the model can be improved using hard-negative examples and additional fine-tuning.

⸻

🧰 Tech Stack

Technology	Purpose
Python 3.11	Core application
YOLO / Ultralytics	Object detection
OpenCV	Computer vision and video processing
PyGame	Audio alerts
NumPy	Numerical processing
Git / GitHub	Version control

⸻

📁 Project Structure

DriverSafetyAI/
│
├── app.py
├── train.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── config/
│   └── config.py
│
├── src/
│   ├── __init__.py
│   ├── detector.py
│   ├── motion_detector.py
│   ├── violation_manager.py
│   ├── audio_alert.py
│   ├── visualization.py
│   └── roi.py
│
├── audio/
│   └── warning.wav
│
└── models/
    └── best.pt

Note: The trained model and large datasets are not stored directly in the normal Git repository. The source code and training pipeline are included, while large ML assets can be distributed separately.

⸻

 Installation

1. Clone the Repository

git clone https://github.com/pranjul075/DriverSafetyAI.git
cd DriverSafetyAI

2. Create a Python 3.11 Environment

python3.11 -m venv venv

Activate it on macOS/Linux:

source venv/bin/activate

Windows:

venv\Scripts\activate

3. Install Dependencies

pip install -r requirements.txt

⸻

🤖 Model Setup

The application uses a trained YOLO model located at:

models/best.pt

If the model is distributed separately, download it and place it inside the models directory:

DriverSafetyAI/
└── models/
    └── best.pt

The trained model contains the following classes:

0 → smoking
1 → phone
2 → seatbelt

Large trained models and datasets are intentionally excluded from normal Git commits to keep the repository lightweight.

⸻

▶ Run the Application

Webcam

python3.11 app.py --source 0

Video File

python3.11 app.py --source driving.mp4

⸻

⌨️ Controls

Key	Action
Q	Quit application
SPACE	Pause / Resume

⸻

 Configuration

System parameters are centralized in:

config/config.py

Important parameters include:

CONFIDENCE_THRESHOLD = 0.80
CONFIRMATION_TIME = 2.0
WARNING_COOLDOWN = 1.0

Confidence Threshold

Controls the minimum YOLO confidence required for a detection.

Higher values generally reduce weak detections but may also cause valid detections to be missed.

Confirmation Time

Controls how long a detection must remain continuously present before becoming a confirmed violation.

Warning Cooldown

Controls how frequently the audio warning can be triggered while a violation remains active.

⸻

🧩 Project Architecture

app.py

Main application entry point.

Connects:

* YOLO detector
* Motion detector
* Violation manager
* Audio alert system
* Visualization

src/detector.py

Responsible for:

* Loading the trained YOLO model
* Running inference
* Extracting bounding boxes
* Extracting class IDs
* Applying confidence filtering

src/violation_manager.py

Responsible for:

* Tracking detections over time
* Temporal confirmation
* Violation state management
* Combined violation detection
* Warning cooldown

src/motion_detector.py

Analyzes frame changes to determine whether the vehicle appears to be moving.

src/audio_alert.py

Responsible for:

* Loading the warning sound
* Playing audio alerts
* Handling audio playback without blocking the main processing loop

src/visualization.py

Responsible for:

* Bounding boxes
* Status information
* Warning banners
* Detection visualization

config/config.py

Central configuration for:

* Model path
* Detection classes
* Confidence threshold
* Confirmation time
* Warning cooldown
* Display settings

⸻

🧪 Model Training

The project includes training utilities in:

train.py

The model can be trained using a YOLO-compatible dataset containing:

dataset/
├── train/
│   ├── images/
│   └── labels/
│
├── valid/
│   ├── images/
│   └── labels/
│
├── test/
│   ├── images/
│   └── labels/
│
└── data.yaml

For improving false positives, additional negative and hard-negative examples can be introduced during fine-tuning.

For example, if a pen is incorrectly classified as smoking, images containing pens without smoking objects can be added as negative training examples.

⸻

 Improving the Model

Possible improvements include:

* Adding hard-negative examples
* Adding more real-world driver images
* Increasing dataset diversity
* Improving camera-angle coverage
* Testing different confidence thresholds
* Fine-tuning the existing trained model
* Adding object tracking
* Improving temporal filtering
* Evaluating precision and recall

The goal is to improve real-world robustness rather than simply increasing the confidence threshold.

⸻

💡 Engineering Highlights

DriverSafetyAI combines machine-learning inference with traditional application logic.

Real-Time Processing

Processes webcam frames continuously using OpenCV and YOLO.

Temporal Reasoning

A single-frame prediction does not immediately trigger a violation.

Event-Based Alerts

Audio warnings are triggered only after the violation manager confirms a violation.

Modular Design

Detection, motion analysis, violation logic, audio, and visualization are separated into independent modules.

Configurable Behavior

Important system parameters can be adjusted through the central configuration file.

⸻

⚠️ Limitations

Detection performance depends on:

* Camera quality
* Lighting conditions
* Camera angle
* Dataset quality
* Model training quality
* Object visibility
* Detection confidence

This project is intended as an AI/computer-vision research and portfolio project and should not be considered a certified automotive safety system.

⸻

Project

GitHub: https://github.com/pranjul075/DriverSafetyAI

If you find the project interesting, feel free to explore the source code and experiment with the detection and violation-management pipeline.

Built with Python, YOLO, OpenCV, and a focus on practical AI engineering.