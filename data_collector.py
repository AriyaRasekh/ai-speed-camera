import cv2
import time
from pathlib import Path
from datetime import datetime


# ============================================================
# CAMERA CONFIGURATION
# ============================================================

CAMERA_INDEX = 0

WIDTH = 1920
HEIGHT = 1080
FPS = 30

# Manual focus value
FOCUS = 128.0


# ============================================================
# ROI CONFIGURATION
# ============================================================

# ROI bounding box: x1, y1, x2, y2
# Top-left point:     (0, 585)
# Bottom-right point: (1235, 715)

ROI_X1 = 0
ROI_Y1 = 585

ROI_X2 = 1235
ROI_Y2 = 715

# ROI size
ROI_WIDTH = ROI_X2 - ROI_X1
ROI_HEIGHT = ROI_Y2 - ROI_Y1

ROI_X = ROI_X1
ROI_Y = ROI_Y1


# ============================================================
# MOTION DETECTION CONFIGURATION
# ============================================================

# Minimum time between saved images
COOL_DOWN = 0.2

# Pixel difference threshold
# Lower = more sensitive to movement
DIFF_THRESHOLD = 15

# Minimum changed area required to trigger capture
# Lower value allows detection of smaller moving objects
MIN_MOTION_AREA = 100

# Smaller blur preserves small moving objects
BLUR_SIZE = (5, 5)


# ============================================================
# OUTPUT CONFIGURATION
# ============================================================

# Create "images" folder next to this Python script
SAVE_DIR = Path(__file__).resolve().parent / "images"

# Create folder automatically if it doesn't exist
SAVE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Open camera
    # --------------------------------------------------------

    cap = cv2.VideoCapture(
        CAMERA_INDEX,
        cv2.CAP_V4L2
    )

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open camera index {CAMERA_INDEX}"
        )

    # --------------------------------------------------------
    # Configure camera
    # --------------------------------------------------------

    # MJPEG
    cap.set(
        cv2.CAP_PROP_FOURCC,
        cv2.VideoWriter_fourcc(*"MJPG")
    )

    # Resolution
    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        WIDTH
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        HEIGHT
    )

    # FPS
    cap.set(
        cv2.CAP_PROP_FPS,
        FPS
    )

    # Disable autofocus
    cap.set(
        cv2.CAP_PROP_AUTOFOCUS,
        0
    )

    # Set manual focus
    cap.set(
        cv2.CAP_PROP_FOCUS,
        FOCUS
    )

    # --------------------------------------------------------
    # Get actual camera configuration
    # --------------------------------------------------------

    actual_width = int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    actual_height = int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    actual_fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    actual_focus = cap.get(
        cv2.CAP_PROP_FOCUS
    )

    print()
    print("========================================")
    print(" Camera Configuration")
    print("========================================")
    print(f"Resolution : {actual_width}x{actual_height}")
    print(f"FPS        : {actual_fps}")
    print(f"Focus      : {actual_focus}")
    print(
        f"ROI        : "
        f"({ROI_X1}, {ROI_Y1}) -> "
        f"({ROI_X2}, {ROI_Y2})"
    )
    print(f"ROI Size   : {ROI_WIDTH}x{ROI_HEIGHT}")
    print(f"Cooldown   : {COOL_DOWN}s")
    print(f"Save folder: {SAVE_DIR}")
    print("========================================")
    print()
    print("Controls:")
    print("  A      Decrease focus")
    print("  D      Increase focus")
    print("  S      Manually save frame")
    print("  Q      Quit")
    print("  ESC    Quit")
    print()

    # --------------------------------------------------------
    # Validate ROI
    # --------------------------------------------------------

    if ROI_X1 < 0 or ROI_Y1 < 0:
        raise ValueError(
            "ROI coordinates cannot be negative."
        )

    if ROI_X2 > actual_width:
        raise ValueError(
            "ROI exceeds camera width."
        )

    if ROI_Y2 > actual_height:
        raise ValueError(
            "ROI exceeds camera height."
        )

    if ROI_X2 <= ROI_X1 or ROI_Y2 <= ROI_Y1:
        raise ValueError(
            "Invalid ROI coordinates."
        )

    # --------------------------------------------------------
    # Motion detection state
    # --------------------------------------------------------

    previous_roi = None

    last_save_time = 0.0

    motion_detected = False

    # --------------------------------------------------------
    # Create display window
    # --------------------------------------------------------

    cv2.namedWindow(
        "Camera Feed",
        cv2.WINDOW_NORMAL
    )

    # Make display window the same size as the camera image
    cv2.resizeWindow(
        "Camera Feed",
        actual_width,
        actual_height
    )

    # --------------------------------------------------------
    # Main camera loop
    # --------------------------------------------------------

    while True:

        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame.")
            break

        # ----------------------------------------------------
        # Keep a clean copy for saving
        # ----------------------------------------------------

        clean_frame = frame.copy()

        # ----------------------------------------------------
        # Extract ROI
        # ----------------------------------------------------

        roi = frame[
            ROI_Y1:ROI_Y2,
            ROI_X1:ROI_X2
        ]

        # ----------------------------------------------------
        # Convert ROI to grayscale
        # ----------------------------------------------------

        gray_roi = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2GRAY
        )

        # Reduce sensor noise
        gray_roi = cv2.GaussianBlur(
            gray_roi,
            BLUR_SIZE,
            0
        )

        # ----------------------------------------------------
        # Motion detection
        # ----------------------------------------------------

        motion_detected = False
        motion_area = 0

        if previous_roi is not None:

            # Calculate difference between current and
            # previous ROI
            frame_delta = cv2.absdiff(
                previous_roi,
                gray_roi
            )

            # Threshold the difference
            threshold = cv2.threshold(
                frame_delta,
                DIFF_THRESHOLD,
                255,
                cv2.THRESH_BINARY
            )[1]

            # Expand detected regions
            threshold = cv2.dilate(
                threshold,
                None,
                iterations=2
            )

            # Find contours
            contours, _ = cv2.findContours(
                threshold,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            for contour in contours:

                area = cv2.contourArea(
                    contour
                )

                if area < MIN_MOTION_AREA:
                    continue

                motion_detected = True
                motion_area += area

                # Draw motion bounding box
                x, y, w, h = cv2.boundingRect(
                    contour
                )

                cv2.rectangle(
                    frame,
                    (
                        ROI_X1 + x,
                        ROI_Y1 + y
                    ),
                    (
                        ROI_X1 + x + w,
                        ROI_Y1 + y + h
                    ),
                    (0, 0, 255),
                    2
                )

        # ----------------------------------------------------
        # Save frame when motion is detected
        # ----------------------------------------------------

        current_time = time.monotonic()

        cooldown_finished = (
            current_time - last_save_time
            >= COOL_DOWN
        )

        if motion_detected and cooldown_finished:

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )

            filename = (
                SAVE_DIR /
                f"capture_{timestamp}.jpg"
            )

            # Save CLEAN frame without overlays
            success = cv2.imwrite(
                str(filename),
                clean_frame
            )

            if success:

                print(
                    f"[CAPTURED] {filename}"
                )

                last_save_time = current_time

            else:

                print(
                    f"[ERROR] Failed to save "
                    f"{filename}"
                )

        # ----------------------------------------------------
        # Update previous ROI
        # ----------------------------------------------------

        previous_roi = gray_roi.copy()

        # ----------------------------------------------------
        # Draw ROI
        # ----------------------------------------------------

        if motion_detected:

            roi_color = (0, 0, 255)

        else:

            roi_color = (0, 255, 0)

        cv2.rectangle(
            frame,
            (ROI_X1, ROI_Y1),
            (ROI_X2, ROI_Y2),
            roi_color,
            3
        )

        # ----------------------------------------------------
        # Status text
        # ----------------------------------------------------

        if motion_detected:

            status = "MOTION DETECTED"
            status_color = (0, 0, 255)

        else:

            status = "NO MOTION"
            status_color = (0, 255, 0)

        cv2.putText(
            frame,
            status,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            status_color,
            3
        )

        # ----------------------------------------------------
        # Focus display
        # ----------------------------------------------------

        current_focus = cap.get(
            cv2.CAP_PROP_FOCUS
        )

        cv2.putText(
            frame,
            f"Focus: {current_focus:.1f}",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

        # ----------------------------------------------------
        # Cooldown display
        # ----------------------------------------------------

        time_since_save = (
            current_time - last_save_time
        )

        if time_since_save < COOL_DOWN:

            remaining = (
                COOL_DOWN - time_since_save
            )

            cooldown_text = (
                f"Cooldown: {remaining:.1f}s"
            )

        else:

            cooldown_text = "Ready"

        cv2.putText(
            frame,
            cooldown_text,
            (30, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

        # ----------------------------------------------------
        # Controls display
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "A/D: Focus | S: Save | Q: Quit",
            (30, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # ----------------------------------------------------
        # Display frame
        # ----------------------------------------------------

        cv2.imshow(
            "Camera Feed",
            frame
        )

        # ----------------------------------------------------
        # Keyboard input
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        # Decrease focus
        if key == ord("a"):

            current_focus = max(
                0.0,
                current_focus - 1.0
            )

            cap.set(
                cv2.CAP_PROP_FOCUS,
                current_focus
            )

            print(
                f"Focus: {current_focus:.1f}"
            )

        # Increase focus
        elif key == ord("d"):

            current_focus += 1.0

            cap.set(
                cv2.CAP_PROP_FOCUS,
                current_focus
            )

            print(
                f"Focus: {current_focus:.1f}"
            )

        # Manual save
        elif key == ord("s"):

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )

            filename = (
                SAVE_DIR /
                f"manual_{timestamp}.jpg"
            )

            success = cv2.imwrite(
                str(filename),
                clean_frame
            )

            if success:

                print(
                    f"[MANUAL SAVE] {filename}"
                )

            else:

                print(
                    f"[ERROR] Failed to save "
                    f"{filename}"
                )

        # Quit
        elif key == ord("q") or key == 27:

            break

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    cap.release()
    cv2.destroyAllWindows()

    print()
    print("Camera stopped.")
    print(f"Images saved in: {SAVE_DIR}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
