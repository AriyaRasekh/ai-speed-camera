import os
import sys
import termios
import tty
from datetime import datetime
from pathlib import Path

import cv2


SAVING_DIR = "focus_calibration_images" # saves frame in this format image_focus_[FOCUS_VALUE]_[DATA_TIME].jpg e.g. image_focus_73.0_20260810_083412_123456.jpg
CAMERA_INDEX = 0
WIDTH = 1920
HEIGHT = 1080
FPS = 60
INITIAL_FOCUS = 50.0

COARSE_FOCUS_STEP = 10.0
FINE_FOCUS_STEP = 1.0


class TerminalKeys:
    """Read single keypresses from an SSH/terminal session without Enter."""

    def __init__(self):
        self.fd = None
        self.old_settings = None

    def __enter__(self):
        if not sys.stdin.isatty():
            raise RuntimeError(
                "stdin is not a terminal. Run this script from an interactive "
                "SSH session so single-key controls are available."
            )

        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)

        # cbreak gives immediate single-character input while still allowing
        # terminal-generated signals such as Ctrl+C.
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.fd is not None and self.old_settings is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def read_key(self):
        """Return one pending key, or None without blocking camera capture."""
        import select

        readable, _, _ = select.select([self.fd], [], [], 0)
        if not readable:
            return None

        data = os.read(self.fd, 1)
        if not data:
            return None

        return data.decode(errors="ignore")


def set_focus(cap, requested_focus):
    """Set manual focus and return the value reported back by the camera."""
    requested_focus = max(0.0, float(requested_focus))
    ok = cap.set(cv2.CAP_PROP_FOCUS, requested_focus)
    actual_focus = cap.get(cv2.CAP_PROP_FOCUS)

    if not ok:
        print(f"Warning: camera rejected focus request {requested_focus:.1f}")

    return actual_focus


def save_frame(frame, save_dir, focus):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = save_dir / f"image_focus_{focus:.1f}_{timestamp}.jpg"

    if cv2.imwrite(str(filename), frame):
        print(f"Saved: {filename}")
    else:
        print(f"Failed to save: {filename}")


def main():
    save_dir = Path(__file__).resolve().parent / SAVING_DIR
    save_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}")

    try:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, FPS)

        # Manual focus.
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        focus = set_focus(cap, INITIAL_FOCUS)

        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = cap.get(cv2.CAP_PROP_FPS)

        print(f"Resolution : {actual_width}x{actual_height}")
        print(f"FPS        : {actual_fps:.2f}")
        print(f"Focus      : {focus:.1f}")
        print(f"Save folder: {save_dir}")
        print()
        print("Controls (no Enter required):")
        print("  A / a   focus -10")
        print("  D / d   focus +10")
        print("  Q / q   focus -1")
        print("  E / e   focus +1")
        print("  S / s   save current frame")
        print("  X / x   quit")
        print("  Ctrl+C  quit")
        print()

        with TerminalKeys() as keyboard:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("Failed to read frame.")
                    break

                # Drain all currently queued keystrokes. This prevents rapid
                # focus adjustments from building up while frames are captured.
                while True:
                    key = keyboard.read_key()
                    if key is None:
                        break

                    key = key.lower()

                    if key == "a":
                        focus = set_focus(cap, focus - COARSE_FOCUS_STEP)
                        print(f"Focus: {focus:.1f}")

                    elif key == "d":
                        focus = set_focus(cap, focus + COARSE_FOCUS_STEP)
                        print(f"Focus: {focus:.1f}")

                    elif key == "q":
                        focus = set_focus(cap, focus - FINE_FOCUS_STEP)
                        print(f"Focus: {focus:.1f}")

                    elif key == "e":
                        focus = set_focus(cap, focus + FINE_FOCUS_STEP)
                        print(f"Focus: {focus:.1f}")

                    elif key == "s":
                        save_frame(frame, save_dir, focus)

                    elif key == "x":
                        return

    except KeyboardInterrupt:
        print("\nExiting.")

    finally:
        cap.release()


if __name__ == "__main__":
    main()
