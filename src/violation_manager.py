# src/violation_manager.py
# ─────────────────────────────────────────────
# Violation Manager module
#
# This module handles the LOGIC of deciding
# whether a real violation has occurred.
#
# It solves two problems:
# 1. TEMPORAL CONFIRMATION — don't trigger on
#    a single frame detection, wait for several
#    seconds of continuous detection
# 2. COOLDOWN — don't spam warnings repeatedly,
#    wait before allowing another warning
# ─────────────────────────────────────────────

import time
from config.config import (
    CLASS_PHONE,
    CLASS_SMOKER,
    CLASS_SEATBELT,
    CONFIRMATION_TIME,
    WARNING_COOLDOWN
)

# Violation state constants
# These are the four possible states the system can be in
NORMAL = "NORMAL"
PHONE_VIOLATION = "PHONE_VIOLATION"
SMOKING_VIOLATION = "SMOKING_VIOLATION"
SEATBELT_VIOLATION = "SEATBELT_VIOLATION"
PHONE_SMOKING_VIOLATION = "PHONE_SMOKING_VIOLATION"
PHONE_SEATBELT_VIOLATION = "PHONE_SEATBELT_VIOLATION"
SMOKING_SEATBELT_VIOLATION = "SMOKING_SEATBELT_VIOLATION"
ALL_VIOLATION = "ALL_VIOLATION"


class ViolationManager:
    """
    Tracks detections over time and decides when
    a real violation has been confirmed.

    Key concepts:
    - detection_start_time: when did we FIRST see this detection?
    - If detection is continuous for CONFIRMATION_TIME seconds → violation
    - If detection disappears → reset the timer
    - After warning plays → cooldown period before next warning
    """

    def __init__(self):
        # Track when each class was FIRST continuously detected
        # Key: class_id, Value: timestamp when detection started
        self.detection_start = {
            CLASS_PHONE: None,
            CLASS_SMOKER: None,
            CLASS_SEATBELT: None,
        }

        # Track which classes are currently confirmed violations
        self.confirmed = {
            CLASS_PHONE: False,
            CLASS_SMOKER: False,
            CLASS_SEATBELT: False,
        }

        # Track when the last warning was played (for cooldown)
        self.last_warning_time = 0

        # Current violation state
        self.current_state = NORMAL

        print("ViolationManager initialized")
        print(f"  Confirmation time: {CONFIRMATION_TIME}s")
        print(f"  Warning cooldown: {WARNING_COOLDOWN}s")

    def update(self, driver_detections, vehicle_moving):
        """
        Update violation state based on current detections.

        Called every frame with the list of detections
        that are inside the Driver ROI.

        Args:
            driver_detections: list of Detection objects inside ROI
            vehicle_moving: bool — is the vehicle moving?

        Returns:
            current_state: one of the violation state constants
            should_warn: bool — should audio warning play now?
        """
        now = time.time()

        # Get the set of class IDs currently detected in this frame
        detected_classes = {d.class_id for d in driver_detections}

        # ── TEMPORAL CONFIRMATION LOGIC ────────────────
        for class_id in [CLASS_PHONE, CLASS_SMOKER, CLASS_SEATBELT]:

            if class_id in detected_classes:
                # This class IS detected in this frame

                if self.detection_start[class_id] is None:
                    # First time we're seeing this — start the timer
                    self.detection_start[class_id] = now

                # How long has this been continuously detected?
                elapsed = now - self.detection_start[class_id]

                # If detected for long enough → confirmed violation
                if elapsed >= CONFIRMATION_TIME:
                    self.confirmed[class_id] = True

            else:
                # This class is NOT detected in this frame
                # Reset the timer — detection was not continuous
                self.detection_start[class_id] = None
                self.confirmed[class_id] = False

        # ── DETERMINE VIOLATION STATE ──────────────────
        # Only trigger violations if vehicle is MOVING
        # (or if seatbelt is missing — that matters even when stopped)
        phone = self.confirmed[CLASS_PHONE] and vehicle_moving
        smoke = self.confirmed[CLASS_SMOKER] and vehicle_moving
        belt = self.confirmed[CLASS_SEATBELT]  # seatbelt always matters

        # Determine combined state
        if phone and smoke and belt:
            self.current_state = ALL_VIOLATION
        elif phone and smoke:
            self.current_state = PHONE_SMOKING_VIOLATION
        elif phone and belt:
            self.current_state = PHONE_SEATBELT_VIOLATION
        elif smoke and belt:
            self.current_state = SMOKING_SEATBELT_VIOLATION
        elif phone:
            self.current_state = PHONE_VIOLATION
        elif smoke:
            self.current_state = SMOKING_VIOLATION
        elif belt:
            self.current_state = SEATBELT_VIOLATION
        else:
            self.current_state = NORMAL

        # ── COOLDOWN CHECK ─────────────────────────────
        # Should we play a warning sound right now?
        should_warn = False

        if self.current_state != NORMAL:
            # Only warn if cooldown period has passed
            time_since_last = now - self.last_warning_time

            if time_since_last >= WARNING_COOLDOWN:
                should_warn = True
                self.last_warning_time = now

        return self.current_state, should_warn

    def get_confirmation_progress(self, class_id):
        """
        Returns how close a detection is to being confirmed.
        Useful for displaying a progress indicator.

        Returns:
            Float between 0.0 and 1.0
            0.0 = just started detecting
            1.0 = fully confirmed violation
        """
        if self.detection_start[class_id] is None:
            return 0.0

        elapsed = time.time() - self.detection_start[class_id]
        progress = min(elapsed / CONFIRMATION_TIME, 1.0)
        return progress

    def reset(self):
        """Reset all violation state — call when video source changes."""
        for class_id in self.detection_start:
            self.detection_start[class_id] = None
            self.confirmed[class_id] = False
        self.current_state = NORMAL
        self.last_warning_time = 0