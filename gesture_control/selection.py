"""Selecao estavel da mao de controle, sem mudar ao reordenar deteccoes."""
from math import hypot


def select_control_hand(hands):
    """Compativel com a selecao antiga usada nos testes v0.2."""
    if not hands:
        return None
    return max(hands, key=lambda hand: hand[9].x)


class HandSelector:
    def __init__(self, max_jump=0.22):
        self.max_jump = max_jump
        self.position = None
        self.lost = False

    def reset(self):
        self.position = None
        self.lost = False

    def select(self, hands):
        if not hands:
            self.lost = True
            return None
        if self.lost:
            # Nao adota uma nova mao silenciosamente apos perda de rastreamento.
            self.position = None
            self.lost = False
            return None
        if self.position is None:
            hand = select_control_hand(hands)
        else:
            hand = min(hands, key=lambda h: hypot(h[9].x - self.position[0], h[9].y - self.position[1]))
            if hypot(hand[9].x - self.position[0], hand[9].y - self.position[1]) > self.max_jump:
                self.reset()
                return None
        self.position = (hand[9].x, hand[9].y)
        return hand
