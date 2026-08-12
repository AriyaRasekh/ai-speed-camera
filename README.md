# Highway Vehicle Data Collection

Data collection utility for a real-time highway speed camera running on an **NVIDIA Jetson Orin Nano 8GB**.

Instead of saving every frame from the camera, the collector watches only the road area and saves an image when meaningful motion is detected. This produces a cleaner training dataset with fewer empty and repetitive frames.

![Highway data collection demo](assets/data_collection_demo.gif)

## Key Features

- **1080p / 60 FPS capture**
- **Road-only ROI** to ignore irrelevant parts of the scene
- **Motion-triggered saving** so useful frames are captured automatically
- **Noise filtering** to avoid false triggers from small pixel changes
- **Cooldown between captures** to reduce duplicate images of the same vehicle
- **Manual focus control** for a fixed highway camera
- **Clean dataset images** — preview boxes and status text are never written to saved frames

The motion detection is intentionally lightweight. It compares consecutive frames inside the road ROI rather than running a neural network just to decide when to save an image. This keeps data collection fast and inexpensive on the Jetson.

## Run

```bash
python3 data_collector.py
```

Controls:

```text
A / D   Adjust focus
S       Save current frame manually
Q       Quit
ESC     Quit
```

Captured images are written automatically to the `images/` directory.
