# src/audio_alert.py
# ─────────────────────────────────────────────
# Audio Alert module
#
# Plays a warning sound when a violation is confirmed.
#
# We use pygame for audio playback because it:
# - Works on Mac, Windows, Linux
# - Can play WAV files easily
# - Doesn't block the main video loop
#
# If pygame is not installed:
# pip install pygame
# ─────────────────────────────────────────────

import os
import threading
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

# Try to import pygame for audio
# If it fails, we fall back to a simple beep
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
    print("Audio: pygame initialized successfully")
except ImportError:
    PYGAME_AVAILABLE = False
    print("Audio: pygame not found — using fallback beep")


def generate_warning_wav():
    """
    Generates a simple beep WAV file programmatically.
    This means you don't need an external audio file —
    the system creates one automatically if missing.

    The beep is a pure sine wave tone.
    """
    import struct
    import math

    # WAV file parameters
    sample_rate = 44100   # samples per second (CD quality)
    frequency = 880       # Hz — a high-pitched beep (A5 note)
    duration = 0.6        # seconds
    volume = 0.7          # 0.0 to 1.0

    num_samples = int(sample_rate * duration)

    # Generate sine wave samples
    samples = []
    for i in range(num_samples):
        # Sine wave formula: sin(2π × frequency × time)
        sample = volume * math.sin(2 * math.pi * frequency * i / sample_rate)
        # Convert to 16-bit integer (-32768 to 32767)
        sample_int = int(sample * 32767)
        samples.append(sample_int)

    # Write WAV file
    os.makedirs("audio", exist_ok=True)

    with open(AUDIO_WARNING_PATH, "wb") as f:
        # WAV header
        num_channels = 1        # mono
        bits_per_sample = 16
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        block_align = num_channels * bits_per_sample // 8
        data_size = num_samples * block_align

        # RIFF chunk
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")

        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))           # chunk size
        f.write(struct.pack("<H", 1))            # PCM format
        f.write(struct.pack("<H", num_channels))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", byte_rate))
        f.write(struct.pack("<H", block_align))
        f.write(struct.pack("<H", bits_per_sample))

        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        for sample in samples:
            f.write(struct.pack("<h", sample))

    print(f"Warning WAV generated: {AUDIO_WARNING_PATH}")


class AudioAlert:
    """
    Manages audio warnings for driver violations.

    Plays a beep sound in a separate thread so it
    doesn't freeze the video feed while playing.
    """

    def __init__(self):
        # Make sure the warning WAV file exists
        if not os.path.exists(AUDIO_WARNING_PATH):
            print("Warning WAV not found — generating one...")
            generate_warning_wav()

        # Load the sound if pygame is available
        self.sound = None
        if PYGAME_AVAILABLE:
            try:
                self.sound = pygame.mixer.Sound(AUDIO_WARNING_PATH)
                print(f"Audio loaded: {AUDIO_WARNING_PATH}")
            except Exception as e:
                print(f"Audio load error: {e}")

        print("AudioAlert initialized")

    def play(self, violation_state):
        """
        Play a warning sound for the given violation state.
        Runs in a separate thread so video keeps playing.

        Args:
            violation_state: one of the violation state constants
        """
        if violation_state == NORMAL:
            return

        # Get the warning message for this violation
        message = self._get_message(violation_state)
        print(f"⚠️  AUDIO WARNING: {message}")

        # Play sound in a separate thread
        # This prevents audio from blocking the video loop
        thread = threading.Thread(
            target=self._play_sound,
            daemon=True  # thread dies when main program exits
        )
        thread.start()

    def _play_sound(self):
        """
        Internal method that actually plays the sound.
        Runs in a background thread.
        """
        if PYGAME_AVAILABLE and self.sound:
            try:
                self.sound.play()
            except Exception as e:
                print(f"Audio playback error: {e}")
        else:
            # Fallback: print a beep character to terminal
            print("\a")  # \a is the ASCII bell character

    def _get_message(self, violation_state):
        """
        Returns a human readable message for each violation type.
        """
        messages = {
            PHONE_VIOLATION: "Phone detected while driving!",
            SMOKING_VIOLATION: "Smoking detected while driving!",
            SEATBELT_VIOLATION: "Seatbelt not detected!",
            PHONE_SMOKING_VIOLATION: "Phone AND smoking detected!",
            PHONE_SEATBELT_VIOLATION: "Phone detected — no seatbelt!",
            SMOKING_SEATBELT_VIOLATION: "Smoking detected — no seatbelt!",
            ALL_VIOLATION: "Phone, smoking AND no seatbelt!",
        }
        return messages.get(violation_state, "Violation detected!")