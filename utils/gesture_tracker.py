"""Shared single-hand input for the four mini games."""

from dataclasses import dataclass
from math import hypot
from pathlib import Path
from time import monotonic_ns

import cv2
import mediapipe as mp


@dataclass(frozen=True)
class HandInput:
    tracked: bool = False
    x: float | None = None
    y: float | None = None
    pinched: bool = False
    pressed: bool = False
    released: bool = False
    points: tuple = ()


class GestureTracker:
    def __init__(self, model_path):
        model_path = Path(model_path)
        if not model_path.is_file():
            raise FileNotFoundError(f"Download the model to {model_path} (see setup instructions).")
        vision = mp.tasks.vision
        self.detector = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=1,
            )
        )
        self.last_time = -1
        self.input = HandInput()

    def update(self, frame):
        """Read an OpenCV BGR frame. Coordinates follow the input frame."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self.last_time = max(self.last_time + 1, monotonic_ns() // 1_000_000)
        hands = self.detector.detect_for_video(image, self.last_time).hand_landmarks
        if not hands:
            self.input = HandInput()
            return self.input

        points = tuple((point.x, point.y) for point in hands[0])
        height, width = frame.shape[:2]
        aspect = width / height

        def distance(a, b):
            return hypot((points[a][0] - points[b][0]) * aspect, points[a][1] - points[b][1])

        previous = self.input
        ratio = distance(4, 8) / max(distance(0, 9), 0.001)
        pinched = ratio < (0.45 if previous.pinched else 0.32)
        x = sum(points[index][0] for index in (0, 5, 9, 17)) / 4
        y = sum(points[index][1] for index in (0, 5, 9, 17)) / 4
        if previous.tracked:
            x = previous.x + 0.28 * (x - previous.x)
            y = previous.y + 0.28 * (y - previous.y)
        self.input = HandInput(True, x, y, pinched, pinched and not previous.pinched,
                               previous.pinched and not pinched, points)
        return self.input

    def close(self):
        self.detector.close()
