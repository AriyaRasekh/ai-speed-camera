
import cv2
from pathlib import Path
from datetime import datetime


CAMERA_INDEX = 0
WIDTH = 1920
HEIGHT = 1080
FPS = 60

FOCUS_STEP = 10.0
INITIAL_FOCUS = 50.0


def main():
    # Folder containing this Python script
    save_dir = Path(__file__).resolve().parent

    # Open camera using V4L2
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}")

    # Configure camera
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    # Disable autofocus
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

    # Set initial focus
    cap.set(cv2.CAP_PROP_FOCUS, INITIAL_FOCUS)

    # Print actual configuration
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    actual_focus = cap.get(cv2.CAP_PROP_FOCUS)

    print(f"Resolution : {actual_width}x{actual_height}")
    print(f"FPS        : {actual_fps}")
    print(f"Focus      : {actual_focus}")
    print(f"Save folder: {save_dir}")
    print()
    print("Controls:")
    print("  A      decrease focus")
    print("  D      increase focus")
    print("  S      save image")
    print("  Q/ESC  quit")

    cv2.namedWindow("Camera Feed", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame.")
            break

        focus = cap.get(cv2.CAP_PROP_FOCUS)

        # Display information
        cv2.putText(
            frame,
            f"Focus: {focus:.1f}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2,
        )

        cv2.putText(
            frame,
            "A/D: Focus | S: Save | Q: Quit",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        cv2.imshow("Camera Feed", frame)

        key = cv2.waitKey(1) & 0xFF

        # Decrease focus
        if key == ord("a"):
            focus = max(0.0, focus - FOCUS_STEP)
            cap.set(cv2.CAP_PROP_FOCUS, focus)
            print(f"Focus: {focus:.1f}")

        # Increase focus
        elif key == ord("d"):
            focus += FOCUS_STEP
            cap.set(cv2.CAP_PROP_FOCUS, focus)
            print(f"Focus: {focus:.1f}")

        # Save image
        elif key == ord("s"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = save_dir / f"image_{timestamp}.jpg"

            success = cv2.imwrite(str(filename), frame)

            if success:
                print(f"Saved: {filename}")
            else:
                print(f"Failed to save: {filename}")

        # Quit
        elif key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

