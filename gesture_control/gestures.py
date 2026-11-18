"""Classificador geométrico, sem depender do MediaPipe nos testes."""
from dataclasses import dataclass
from math import hypot

@dataclass(frozen=True)
class Gesture:
    name: str
    x: float = 0.0
    y: float = 0.0


def distance(a, b):
    return hypot(a.x-b.x, a.y-b.y)


def classify(points):
    if points is None:
        return Gesture('none')
    wrist = points[0]
    center = points[9]
    palm = max(distance(points[5], points[17]), 1e-5)
    extended = []
    for tip, pip, mcp in ((8,6,5),(12,10,9),(16,14,13),(20,18,17)):
        # Distância relativa ao nó de base: tolera rotação no plano da imagem.
        extended.append(distance(points[tip], points[mcp]) >
                        distance(points[pip], points[mcp]) * 1.35)
    pinch = distance(points[4], points[8]) < palm * 0.38
    if pinch:
        return Gesture('pinch', center.x, center.y)
    if all(extended):
        return Gesture('open_palm', center.x, center.y)
    if not any(extended):
        return Gesture('fist', center.x, center.y)
    if extended == [True, True, False, False]:
        return Gesture('victory', center.x, center.y)
    return Gesture('neutral', center.x, center.y)
