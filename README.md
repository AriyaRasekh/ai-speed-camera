# Highway Vehicle Data Collection

Lightweight data collection for a real-time speed camera running on an **NVIDIA Jetson Orin Nano 8GB**.

The camera continuously watches the highway, but only saves frames when something moves through the road area. This avoids filling the dataset with empty road and nearly identical frames.

## Demo

![Highway data collection demo](assets/data_collection_demo.gif)

## What the collector does

`data_collector.py`:

- captures **1080p / 60 FPS** webcam video
- monitors only the highway ROI
- detects motion using frame-to-frame differences
- saves the original clean frame when traffic is detected
- ignores tiny changes caused by noise
- uses a cooldown to reduce duplicate images
- keeps preview overlays out of the saved dataset

## Why this approach

Running a full object detector just to collect training data would be unnecessary.

Instead, the collector uses a very cheap motion check inside a narrow section of the frame. That makes it fast enough to run continuously on the Jetson while still catching small, distant vehicles.

A small blur removes camera noise, dilation strengthens fragmented motion regions, and manual focus keeps the road consistently sharp as vehicles pass.

## Files

```text
.
├── data_collector.py
└── assets/
    └── data_collection_demo.gif
```
