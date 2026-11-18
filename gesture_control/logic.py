"""Máquina de estados: pausa entre ações e exigência de gesto sustentado."""
from dataclasses import dataclass
from .gestures import Gesture

@dataclass(frozen=True)
class Action:
    name: str
    dx: int = 0
    dy: int = 0

class GestureLogic:
    def __init__(self, dwell=1.2, cooldown=2.0, move_scale=1200.0):
        self.dwell = dwell
        self.cooldown = cooldown
        self.move_scale = move_scale
        self.candidate = None
        self.since = 0.0
        self.last_action = float('-inf')
        self.drag = False
        self.last_pos = None
        self.fired_gesture = None

    def reset(self):
        self.candidate = None
        self.drag = False
        self.last_pos = None
        self.fired_gesture = None

    def update(self, gesture: Gesture, now: float):
        name = gesture.name
        if name == 'pinch':
            self.fired_gesture = None
            self.candidate = None
            if not self.drag:
                if now - self.last_action < self.cooldown:
                    return None
                self.drag = True
                self.last_pos = (gesture.x, gesture.y)
                return Action('drag_start')
            dx = round((gesture.x-self.last_pos[0]) * self.move_scale)
            dy = round((gesture.y-self.last_pos[1]) * self.move_scale)
            self.last_pos = (gesture.x, gesture.y)
            if abs(dx) + abs(dy) < 3:
                return None
            return Action('drag_move', dx, dy)
        if self.drag:
            self.drag = False
            self.last_pos = None
            self.last_action = now
            return Action('drag_stop')
        if name not in ('victory', 'open_palm', 'fist'):
            self.candidate = None
            self.fired_gesture = None
            return None
        if name == self.fired_gesture:
            return None
        self.fired_gesture = None
        if name != self.candidate:
            self.candidate = name
            self.since = now
            return None
        if now - self.since >= self.dwell and now - self.last_action >= self.cooldown:
            self.candidate = None
            self.last_action = now
            self.fired_gesture = name
            return Action({'victory':'open', 'open_palm':'maximize', 'fist':'close'}[name])
        return None
