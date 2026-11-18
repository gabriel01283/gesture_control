from dataclasses import dataclass
import tomllib
from pathlib import Path

@dataclass(frozen=True)
class Config:
    source: str = "0"
    model: str = "models/hand_landmarker.task"
    open_command: str = "kitty"
    move_scale: float = 1200.0
    dwell_seconds: float = 1.2
    cooldown_seconds: float = 2.0
    mirror: bool = True

    @classmethod
    def load(cls, path: str):
        with open(path, 'rb') as file:
            data = tomllib.load(file)
        return cls(**data.get('gesture_control', {}))
