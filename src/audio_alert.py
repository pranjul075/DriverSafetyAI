# src/audio_alert.py

import os
import threading
import pygame

from config.config import AUDIO_WARNING_PATH

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


class AudioAlert:
    """
    Handles warning sounds for DriverSafetyAI.

    A warning is played whenever ViolationManager
    requests an audio warning.
    """

    def __init__(self):

        self.sound = None

        print("Initializing audio...")

        try:

            # Initialize pygame mixer
            pygame.mixer.init()

            print("✅ pygame mixer initialized")

            # Check WAV file
            if not os.path.exists(AUDIO_WARNING_PATH):

                print(
                    f"❌ Warning sound not found: "
                    f"{AUDIO_WARNING_PATH}"
                )

                return

            # Load sound
            self.sound = pygame.mixer.Sound(
                AUDIO_WARNING_PATH
            )

            print(
                f"✅ Audio loaded: "
                f"{AUDIO_WARNING_PATH}"
            )

        except Exception as e:

            print(
                f"❌ Audio initialization error: {e}"
            )

    def play(self, violation_state):

        # Don't play anything for NORMAL
        if violation_state == NORMAL:
            return

        message = self._get_message(
            violation_state
        )

        print(
            f"🔊 AUDIO WARNING: {message}"
        )

        # Play in background thread
        thread = threading.Thread(
            target=self._play_sound,
            daemon=True
        )

        thread.start()

    def _play_sound(self):

        if self.sound is None:

            print(
                "❌ Cannot play audio: "
                "sound was not loaded"
            )

            return

        try:

            channel = self.sound.play()

            if channel is None:

                print(
                    "❌ pygame failed to start "
                    "audio playback"
                )

            else:

                print("✅ BEEP PLAYING")

        except Exception as e:

            print(
                f"❌ Audio playback error: {e}"
            )

    def _get_message(self, violation_state):

        messages = {

            PHONE_VIOLATION:
                "Phone detected while driving!",

            SMOKING_VIOLATION:
                "Smoking detected while driving!",

            SEATBELT_VIOLATION:
                "Seatbelt not detected!",

            PHONE_SMOKING_VIOLATION:
                "Phone AND smoking detected!",

            PHONE_SEATBELT_VIOLATION:
                "Phone detected — no seatbelt!",

            SMOKING_SEATBELT_VIOLATION:
                "Smoking detected — no seatbelt!",

            ALL_VIOLATION:
                "Phone, smoking AND no seatbelt!"
        }

        return messages.get(
            violation_state,
            "Violation detected!"
        )