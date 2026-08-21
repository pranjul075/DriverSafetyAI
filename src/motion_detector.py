# src/motion_detector.py
# ─────────────────────────────────────────────
# Vehicle Motion Detection module
#
# We estimate whether the vehicle is moving by
# analyzing pixel movement between video frames
# using Optical Flow.
#
# IMPORTANT LIMITATION:
# This is camera-based motion estimation — NOT
# a real speedometer. It can be fooled by:
# - Camera shake / bumps
# - Other cars moving beside you
# - Lighting changes
# - Stationary objects passing by
#
# In a real automotive system, this would be
# replaced by GPS speed or OBD-II vehicle speed.
# The design here makes that swap easy to do.
# ─────────────────────────────────────────────

import cv2
import numpy as np
from collections import deque
from config.config import MOTION_THRESHOLD, MOTION_HISTORY_FRAMES


class MotionDetector:
    """
    Detects vehicle motion using Optical Flow.
    
    Optical Flow works by comparing two consecutive
    frames and measuring how much pixels have moved.
    
    If pixels move a lot → vehicle is likely moving
    If pixels barely move → vehicle is likely stopped
    """

    def __init__(self):
        # Store the previous frame for comparison
        self.prev_gray = None

        # Keep a history of recent motion scores
        # deque automatically removes old values when full
        # This smooths out sudden spikes (e.g. one bumpy frame)
        self.motion_history = deque(maxlen=MOTION_HISTORY_FRAMES)

        # Current motion state
        self.is_moving = False

        # The averaged motion score (for display)
        self.current_motion_score = 0.0

        print("MotionDetector initialized")
        print(f"  Threshold: {MOTION_THRESHOLD}")
        print(f"  History frames: {MOTION_HISTORY_FRAMES}")

    def update(self, frame):
        """
        Process a new frame and update the motion estimate.
        
        Call this every frame in your main loop.
        
        Args:
            frame: current OpenCV video frame (BGR color)
        
        Returns:
            is_moving (bool): True if vehicle appears to be moving
        """
        # Convert frame to grayscale
        # Optical flow works on single-channel (grayscale) images
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # On the very first frame, we have nothing to compare to
        if self.prev_gray is None:
            self.prev_gray = gray
            return False

        # Calculate Dense Optical Flow using Farneback algorithm
        # This computes motion vectors for every pixel in the frame
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray,  # previous frame
            gray,            # current frame
            None,            # output (None = create new)
            0.5,             # pyramid scale (0.5 = each layer is half size)
            3,               # number of pyramid layers
            15,              # window size for averaging
            3,               # iterations per pyramid level
            5,               # pixel neighborhood size
            1.2,             # standard deviation for Gaussian
            0                # flags
        )

        # flow has shape (height, width, 2)
        # flow[..., 0] = horizontal movement (x direction)
        # flow[..., 1] = vertical movement (y direction)

        # Calculate the magnitude of movement for each pixel
        # magnitude = sqrt(x_movement² + y_movement²)
        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Average magnitude across all pixels = overall motion score
        motion_score = float(np.mean(magnitude))

        # Add to history for smoothing
        self.motion_history.append(motion_score)

        # Average the recent history to reduce noise
        self.current_motion_score = float(np.mean(self.motion_history))

        # Compare against threshold to decide moving/stopped
        self.is_moving = self.current_motion_score > MOTION_THRESHOLD

        # Update previous frame for next comparison
        self.prev_gray = gray

        return self.is_moving

    def get_status_text(self):
        """
        Returns a human-readable status string for display.
        
        Example: "MOVING (2.34)" or "STOPPED (0.12)"
        """
        status = "MOVING" if self.is_moving else "STOPPED"
        return f"{status} ({self.current_motion_score:.2f})"

    def reset(self):
        """
        Reset the motion detector.
        Call this if the video source changes.
        """
        self.prev_gray = None
        self.motion_history.clear()
        self.is_moving = False
        self.current_motion_score = 0.0

    # ── FUTURE EXTENSION ───────────────────────
    # To replace camera-based motion with GPS or OBD-II speed:
    #
    # def update_from_gps(self, speed_kmh):
    #     self.is_moving = speed_kmh > 5.0
    #     return self.is_moving
    #
    # def update_from_obd(self, vehicle_speed):
    #     self.is_moving = vehicle_speed > 0
    #     return self.is_moving
    #
    # The rest of the pipeline doesn't change at all —
    # only this module needs to be swapped out.