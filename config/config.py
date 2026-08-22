# config/config.py
# ─────────────────────────────────────────────
# Central configuration for DriverSafetyAI
# Change values here to tune the system behavior
# ─────────────────────────────────────────────

import os

# ── MODEL ──────────────────────────────────────
# Path to your trained YOLO model
# After Colab training finishes, download best.pt and put it in models/
MODEL_PATH = os.path.join("models", "best.pt")

# Minimum confidence score to accept a YOLO detection
# 0.0 = accept everything, 1.0 = only perfect detections
# 0.6 is a good starting point — raise it if too many false alarms
CONFIDENCE_THRESHOLD = 0.60

# ── CLASS IDs ──────────────────────────────────
# Must match what your model was trained on
CLASS_PHONE = 0
CLASS_SMOKER = 1
CLASS_SEATBELT = 2

# Human-readable names for display
CLASS_NAMES = {
    CLASS_PHONE: "Phone",
    CLASS_SMOKER: "Smoker",
    CLASS_SEATBELT: "Seatbelt",
}

# ── DRIVER ROI ─────────────────────────────────
# Region of Interest — the rectangular area where the DRIVER sits
# Only detections whose bounding-box CENTER falls inside this box
# will be considered driver violations
# Format: (x1, y1, x2, y2) in pixels
# These are default values — the app will let you select ROI interactively
ROI_DEFAULT = (0, 0, 640, 480)  # full frame as default (replaced at runtime)

# ── TEMPORAL CONFIRMATION ──────────────────────
# How many seconds a detection must be continuously present
# before it triggers a violation alert
# Example: 2.0 means phone must be visible for 2 full seconds
CONFIRMATION_TIME = 2.0  # seconds

# ── AUDIO WARNING ──────────────────────────────
# After a warning plays, wait this many seconds before
# allowing another warning — prevents non-stop beeping
WARNING_COOLDOWN = 1.0  # seconds

# Path to warning sound file
AUDIO_WARNING_PATH = os.path.join("audio", "warning.wav")

# ── VEHICLE MOTION ─────────────────────────────
# Optical flow threshold — how much pixel movement counts as "moving"
# Higher = less sensitive (needs more motion to trigger "moving")
# Lower = more sensitive (small camera shake might trigger "moving")
MOTION_THRESHOLD = 2.0

# How many frames to average motion over (smoothing)
MOTION_HISTORY_FRAMES = 10

# ── VIDEO INPUT ────────────────────────────────
# Default video source
# 0 = webcam, or provide a path like "driving.mp4"
DEFAULT_SOURCE = 0

# Display window size
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
# ── DISPLAY ────────────────────────────────────
# Window title
WINDOW_TITLE = "DriverSafetyAI - Real Time Driver Safety System"

# Font scale for overlay text
FONT_SCALE = 0.6
FONT_THICKNESS = 2