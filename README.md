# AI Speed Camera

A real-time computer vision project running on an **NVIDIA Jetson Orin Nano 8GB**.

A webcam points at the highway, the system detects and tracks vehicles, then estimates their speed based on how far they move over time.

## Data Collection

The first step is building a useful vehicle dataset.

`data_collector.py` watches the highway and automatically saves images when motion is detected in the road area.

Instead of saving every video frame, it only captures useful traffic scenes. This reduces empty images, repeated frames, storage use, and annotation work.

## Demo

![Highway data collection demo](assets/data_collection_demo.gif)

## How It Works

- **Road-only detection:** motion is checked only in the part of the image where vehicles pass.
- **Motion-triggered capture:** images are saved when a vehicle enters the monitored area.
- **Lightweight processing:** simple frame differences are used instead of running an AI model during data collection.
- **Clean saved images:** boxes and status text are shown only in the live preview and are not saved into the dataset.
- **Manual focus:** keeps the highway consistently sharp instead of allowing autofocus to change as vehicles pass.
- **Capture cooldown:** reduces repeated images of the same vehicle.

## Project Pipeline

```text
Webcam
  ↓
Collect highway images
  ↓
Label vehicles
  ↓
Train vehicle detector
  ↓
Track vehicles
  ↓
Estimate vehicle speed
```

## Hardware

- NVIDIA Jetson Orin Nano 8GB
- USB webcam

## Run

```bash
python3 data_collector.py
```

Captured images are saved automatically into the `images/` folder.

## Repository Structure

```text
.
├── README.md
├── data_collector.py
└── assets/
    └── data_collection_demo.gif
```
