"""Estados dos gestos: liberacao estavel, cooldown e fechamento deliberado."""
from dataclasses import dataclass
from .gestures import Gesture


@dataclass(frozen=True)
class Action:
    name: str
    dx: int = 0
    dy: int = 0


class GestureLogic:
    def __init__(self, dwell=1.2, cooldown=2.0, move_scale=1200.0,
                 release_seconds=0.4, close_dwell=None):
        self.dwell = dwell
        self.cooldown = cooldown
        self.move_scale = move_scale
        self.release_seconds = release_seconds
        self.close_dwell = max(close_dwell if close_dwell is not None else dwell, dwell)
        self.last_action = float('-inf')
        self.reset()

    def reset(self):
        self.candidate = None
        self.since = 0.0
        self.drag = False
        self.last_pos = None
        self.fired_gesture = None
        self.release_since = None
        self.require_release = False

    def suspend(self):
        """Interrompe comandos apos perda de mao; exige gesto neutro para rearmar."""
        self.reset()
        self.require_release = True

    def update(self, gesture: Gesture, now: float):
        name = gesture.name
        if self.drag:
            if name == 'pinch':
                dx = round((gesture.x - self.last_pos[0]) * self.move_scale)
                dy = round((gesture.y - self.last_pos[1]) * self.move_scale)
                self.last_pos = (gesture.x, gesture.y)
                if abs(dx) + abs(dy) < 3:
                    return None
                return Action('drag_move', dx, dy)
            self.drag = False
            self.last_pos = None
            self.last_action = now
            self.require_release = True
            self.release_since = None
            self.candidate = None
            return Action('drag_stop')

        # Apos uma acao, somente um gesto neutro sustentado libera nova acao.
        # Oscilacoes curtas de reconhecimento nao contam como liberacao.
        if self.require_release:
            if name in ('neutral', 'none'):
                if self.release_since is None:
                    self.release_since = now
                elif now - self.release_since >= self.release_seconds:
                    self.require_release = False
                    self.release_since = None
                    self.fired_gesture = None
            else:
                self.release_since = None
            self.candidate = None
            return None

        if name == 'pinch':
            self.candidate = None
            if now - self.last_action < self.cooldown:
                return None
            self.drag = True
            self.last_pos = (gesture.x, gesture.y)
            return Action('drag_start')

        if name not in ('victory', 'open_palm', 'fist'):
            self.candidate = None
            return None
        if name != self.candidate:
            self.candidate = name
            self.since = now
            return None
        hold = self.close_dwell if name == 'fist' else self.dwell
        if now - self.since >= hold and now - self.last_action >= self.cooldown:
            self.last_action = now
            self.candidate = None
            self.fired_gesture = name
            self.require_release = True
            self.release_since = None
            return Action({'victory': 'open', 'open_palm': 'maximize', 'fist': 'close'}[name])
        return None
