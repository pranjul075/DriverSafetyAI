# DriverSafetyAI 🚗

An AI-powered driver safety monitoring system using an inside-car camera.
Detects dangerous driver behaviors in real-time and triggers audio warnings.

## What it detects
- 📱 Mobile phone usage while driving
- 🚬 Smoking while driving  
- 🪑 Seatbelt not worn
- All combinations simultaneously (phone + smoking, etc.)

## How it works
Camera Feed
↓
Vehicle Motion Detection (Optical Flow)
↓
Driver ROI Filter (ignore passengers)
↓
YOLO11 Detection (phone / smoker / seatbelt)
↓
Temporal Confirmation (2 seconds continuous)
↓
Violation Detected
↓
Audio Warning + Visual Alert

## Project Structure
DriverSafetyAI/
├── models/
│ └── best.pt # Trained YOLO11n model
├── config/
│ ├── config.py # All system parameters
│ └── roi.json # Saved Driver ROI coordinates
├── src/
│ ├── detector.py # YOLO detection wrapper
│ ├── roi.py # Driver ROI selection and filtering
│ ├── motion_detector.py # Optical flow vehicle motion detection
│ ├── violation_manager.py # Temporal confirmation and violation logic
│ ├── audio_alert.py # Audio warning system
│ └── visualization.py # OpenCV drawing and display
├── audio/
│ └── warning.wav # Auto-generated warning beep
├── app.py # Main application entry point
├── requirements.txt
└── README.md

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your trained model
Place your trained `best.pt` file in the `models/` folder.

### 3. Run the app

**Webcam:**
```bash
python app.py --source 0
```

**Video file:**
```bash
python app.py --source driving.mp4
```

**Reselect Driver ROI:**
```bash
python app.py --source 0 --select-roi
```

## First Run — ROI Selection
On first run, a window will open showing the camera frame.
Draw a rectangle around the **driver's seat area** and press ENTER.
The ROI is saved automatically — you won't need to redraw it next time.

## Keyboard Controls
| Key | Action |
|-----|--------|
| Q | Quit |
| R | Reselect Driver ROI |
| SPACE | Pause / Resume |

## Violation States
| State | Trigger |
|-------|---------|
| NORMAL | No violations |
| PHONE_VIOLATION | Phone detected while driving |
| SMOKING_VIOLATION | Smoking detected while driving |
| SEATBELT_VIOLATION | No seatbelt detected |
| PHONE_SMOKING_VIOLATION | Phone + smoking simultaneously |
| PHONE_SEATBELT_VIOLATION | Phone + no seatbelt |
| SMOKING_SEATBELT_VIOLATION | Smoking + no seatbelt |
| ALL_VIOLATION | Phone + smoking + no seatbelt |

## Configuration
All parameters are in `config/config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| CONFIDENCE_THRESHOLD | 0.5 | Minimum detection confidence |
| CONFIRMATION_TIME | 2.0s | Seconds before violation confirmed |
| WARNING_COOLDOWN | 5.0s | Seconds between audio warnings |
| MOTION_THRESHOLD | 2.0 | Optical flow sensitivity |

## Technology Stack
- **YOLO11n** — Object detection (Ultralytics)
- **OpenCV** — Video processing, optical flow, visualization
- **PyTorch** — Deep learning backend
- **pygame** — Audio warning playback
- **Python 3.11** — Core language

## Dataset
Trained on the DMS (Driver Monitoring System) dataset from Kaggle.
- 5,957 training images
- 2,389 validation images
- 1,538 test images
- Classes: Phone, Cigarette/Smoker, Seatbelt

## Limitations
This is a **computer vision prototype**, not a certified automotive safety system.

Camera-based motion estimation can be affected by:
- Camera shake or vibration
- Other vehicles moving in frame
- Lighting changes
- Stationary objects passing by

In a production system, vehicle motion would be determined by:
- GPS speed data
- OBD-II vehicle speed sensor
- CAN bus integration

## Future Extensions
- Head pose estimation for drowsiness detection
- Eye state monitoring (open/closed eye)
- GPS/OBD-II speed integration
- Mobile app integration