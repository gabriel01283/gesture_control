import cv2

class Camera:
    def __init__(self, source: str, mirror: bool = True):
        self.source = int(source) if source.isdecimal() else source
        self.mirror = mirror
        self.cap = None

    def __enter__(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir a câmera: {self.source}")
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return self

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        return cv2.flip(frame, 1) if self.mirror else frame

    def __exit__(self, *_):
        if self.cap:
            self.cap.release()
