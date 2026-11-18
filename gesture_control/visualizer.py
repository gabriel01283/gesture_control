"""Desenho opcional dos pontos das maos; nao controla janelas."""
import cv2

CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
)


def draw_debug(frame, hands, gesture_name: str, armed: bool):
    height, width = frame.shape[:2]
    colors = ((0, 255, 0), (255, 255, 0))
    for index, hand in enumerate(hands):
        points = [(int(p.x * width), int(p.y * height)) for p in hand]
        color = colors[index % len(colors)]
        for a, b in CONNECTIONS:
            cv2.line(frame, points[a], points[b], color, 2)
        for point in points:
            cv2.circle(frame, point, 4, (0, 0, 255), -1)

    status = 'SIMULACAO ATIVA' if armed else 'SIMULACAO DESARMADA'
    caption = f'{status} | maos: {len(hands)} | gesto: {gesture_name}'
    cv2.putText(frame, caption, (15, 32), cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (0, 255, 0) if armed else (0, 170, 255), 2)
    return frame
