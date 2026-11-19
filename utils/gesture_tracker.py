"""Compatible replacement for the team's GestureTracker (camera stays in main)."""
from pathlib import Path
from time import monotonic_ns
from .hand_input import HandInput, LandmarkInput

class GestureTracker:
    def __init__(self, model_path):
        path = Path(model_path)
        if not path.is_file():
            raise FileNotFoundError(f'Model missing: {path}. See README.md for the official download.')
        import cv2
        import mediapipe as mp
        self.cv2, self.mp = cv2, mp
        vision = mp.tasks.vision
        self.detector = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(path), delegate=mp.tasks.BaseOptions.Delegate.CPU),
                running_mode=vision.RunningMode.VIDEO, num_hands=1))
        self.last_time = -1
        self.processor = LandmarkInput()
        self.input = HandInput()

    def update(self, frame):
        rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        image = self.mp.Image(image_format=self.mp.ImageFormat.SRGB,data=rgb)
        self.last_time = max(self.last_time+1,monotonic_ns()//1_000_000)
        hands = self.detector.detect_for_video(image,self.last_time).hand_landmarks
        points = tuple((p.x,p.y) for p in hands[0]) if hands else ()
        h,w = frame.shape[:2]
        self.input = self.processor.update(points,w/h)
        return self.input

    def close(self):
        self.detector.close()
