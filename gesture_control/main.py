import argparse
import time
from pathlib import Path
import cv2
from .camera import Camera
from .tracker import HandTracker
from .gestures import classify
from .logic import GestureLogic
from .hyprland import Hyprland
from .config import Config


def main():
    parser = argparse.ArgumentParser(description='Controle gestual de janelas')
    parser.add_argument('--config', default='config.toml')
    parser.add_argument('--source', help='URL de vídeo do tablet ou índice da webcam')
    parser.add_argument('--live', action='store_true', help='Permite comandos reais; exige ativação com tecla A')
    args = parser.parse_args()
    cfg = Config.load(args.config)
    source = args.source or cfg.source
    if not Path(cfg.model).is_file():
        parser.error(f'Modelo ausente: {cfg.model} (veja README)')
    print('Modo:', 'REAL (inicialmente DESARMADO)' if args.live else 'SIMULAÇÃO')
    print('Teclas: A ativa/desativa, Q encerra. Teste com uma janela descartável.')
    backend = Hyprland(live=args.live, command=cfg.open_command)
    logic = GestureLogic(cfg.dwell_seconds, cfg.cooldown_seconds, cfg.move_scale)
    armed = False
    tracker = HandTracker(cfg.model)
    failures = 0
    try:
        with Camera(source, cfg.mirror) as camera:
            while True:
                frame = camera.read()
                if frame is None:
                    failures += 1
                    if failures >= 15:
                        raise RuntimeError('Fluxo de vídeo interrompido')
                    time.sleep(0.08)
                    continue
                failures = 0
                gesture = classify(tracker.detect(frame))
                if armed:
                    action = logic.update(gesture, time.monotonic())
                    if action:
                        print(f'Gesto={gesture.name} ação={action}')
                        try:
                            backend.handle(action)
                        except Exception as e:
                            print(f'Falha no comando: {e}')
                            logic.reset()
                label = f'{"ARMADO" if armed else "DESARMADO"} | {gesture.name} | {"REAL" if args.live else "SIM"}'
                cv2.putText(frame, label, (14, 33), cv2.FONT_HERSHEY_SIMPLEX, .65,
                            (0, 255, 0) if armed else (0, 170, 255), 2)
                cv2.imshow('Gesture Control - A ativa / Q sai', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                if key == ord('a'):
                    armed = not armed
                    logic.reset()
                    backend.drag_target = None
                    print('Ativado' if armed else 'Desativado')
    finally:
        tracker.close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
