"""Politica de seguranca para execucao dos comandos reais."""


def allowed_action(action, live=False, allow_close=False, allow_move=False):
    if action is None:
        return False
    if not live:
        return True
    if action.name == 'close' and not allow_close:
        return False
    if action.name.startswith('drag_') and not allow_move:
        return False
    return True


def safe_gesture(gesture, move_enabled=False):
    """Ignora pinça quando mover não está autorizado, sem iniciar drag bloqueado."""
    if gesture.name == 'pinch' and not move_enabled:
        from .gestures import Gesture
        return Gesture('neutral', gesture.x, gesture.y)
    return gesture
