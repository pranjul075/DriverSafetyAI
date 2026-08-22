# src/violation_manager.py

import time

from config.config import (
    CLASS_PHONE,
    CLASS_SMOKER,
    CLASS_SEATBELT,
    CONFIRMATION_TIME,
    WARNING_COOLDOWN
)



# Violation states


NORMAL = "NORMAL"

PHONE_VIOLATION = "PHONE_VIOLATION"

SMOKING_VIOLATION = "SMOKING_VIOLATION"

SEATBELT_VIOLATION = "SEATBELT_VIOLATION"

PHONE_SMOKING_VIOLATION = \
    "PHONE_SMOKING_VIOLATION"

PHONE_SEATBELT_VIOLATION = \
    "PHONE_SEATBELT_VIOLATION"

SMOKING_SEATBELT_VIOLATION = \
    "SMOKING_SEATBELT_VIOLATION"

ALL_VIOLATION = "ALL_VIOLATION"


class ViolationManager:

    def __init__(self):

        # When each detection started
        self.detection_start = {

            CLASS_PHONE: None,

            CLASS_SMOKER: None,

            CLASS_SEATBELT: None
        }

        # Whether each detection has been
        # continuously confirmed
        self.confirmed = {

            CLASS_PHONE: False,

            CLASS_SMOKER: False,

            CLASS_SEATBELT: False
        }

        # Last time audio warning played
        self.last_warning_time = 0

        # Current state
        self.current_state = NORMAL

        print(
            "ViolationManager initialized"
        )

        print(
            f"  Confirmation time: "
            f"{CONFIRMATION_TIME}s"
        )

        print(
            f"  Warning cooldown: "
            f"{WARNING_COOLDOWN}s"
        )

    # Main update function
    

    def update(
        self,
        driver_detections,
        vehicle_moving
    ):

        now = time.time()

        # Get classes detected in current frame
        detected_classes = {
            d.class_id
            for d in driver_detections
        }


        # TEMPORAL CONFIRMATION


        for class_id in [
            CLASS_PHONE,
            CLASS_SMOKER,
            CLASS_SEATBELT
        ]:

            # Detection exists
            if class_id in detected_classes:

                # Start timer
                if (
                    self.detection_start[class_id]
                    is None
                ):

                    self.detection_start[
                        class_id
                    ] = now

                # Calculate detection duration
                elapsed = (
                    now
                    - self.detection_start[class_id]
                )

                # Confirm after required time
                if elapsed >= CONFIRMATION_TIME:

                    self.confirmed[
                        class_id
                    ] = True

            # Detection disappeared
            else:

                self.detection_start[
                    class_id
                ] = None

                self.confirmed[
                    class_id
                ] = False


        # DETERMINE ACTIVE VIOLATIONS


        phone = (
            self.confirmed[CLASS_PHONE]
            and vehicle_moving
        )

        smoke = (
            self.confirmed[CLASS_SMOKER]
            and vehicle_moving
        )

        belt = (
            self.confirmed[CLASS_SEATBELT]
        )


        # DETERMINE COMBINED STATE


        if phone and smoke and belt:

            self.current_state = ALL_VIOLATION

        elif phone and smoke:

            self.current_state = \
                PHONE_SMOKING_VIOLATION

        elif phone and belt:

            self.current_state = \
                PHONE_SEATBELT_VIOLATION

        elif smoke and belt:

            self.current_state = \
                SMOKING_SEATBELT_VIOLATION

        elif phone:

            self.current_state = \
                PHONE_VIOLATION

        elif smoke:

            self.current_state = \
                SMOKING_VIOLATION

        elif belt:

            self.current_state = \
                SEATBELT_VIOLATION

        else:

            self.current_state = NORMAL


        # AUDIO WARNING


        should_warn = False

        if self.current_state != NORMAL:

            # Time since previous warning
            time_since_warning = (
                now - self.last_warning_time
            )

            # First warning OR cooldown expired
            if (
                self.last_warning_time == 0
                or
                time_since_warning >= WARNING_COOLDOWN
            ):

                should_warn = True

                self.last_warning_time = now

        else:

            # No violation.
            # Reset timer so a new violation
            # can warn immediately.
            self.last_warning_time = 0

        return (
            self.current_state,
            should_warn
        )


    # Confirmation progress


    def get_confirmation_progress(
        self,
        class_id
    ):

        start = self.detection_start[class_id]

        if start is None:

            return 0.0

        elapsed = time.time() - start

        if CONFIRMATION_TIME <= 0:

            return 1.0

        progress = (
            elapsed / CONFIRMATION_TIME
        )

        return min(progress, 1.0)


    # Reset


    def reset(self):

        for class_id in self.detection_start:

            self.detection_start[
                class_id
            ] = None

            self.confirmed[
                class_id
            ] = False

        self.current_state = NORMAL

        self.last_warning_time = 0