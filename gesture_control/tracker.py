import time
import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, model_path: str):
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.last_ms = 0

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp = max(int(time.monotonic() * 1000), self.last_ms + 1)
        self.last_ms = timestamp
        result = self.landmarker.detect_for_video(image, timestamp)
        return result.hand_landmarks[0] if result.hand_landmarks else None

    def close(self):
        self.landmarker.close()
