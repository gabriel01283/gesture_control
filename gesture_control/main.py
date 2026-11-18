"""Gesture Control v0.2.2: duas maos, seguranca e modo real restrito."""
import argparse
import time
from pathlib import Path
import cv2
from .camera import Camera
from .tracker import HandTracker
from .gestures import classify, Gesture
from .logic import GestureLogic
from .hyprland import Hyprland
from .config import Config
from .selection import HandSelector
from .visualizer import draw_debug
from .policy import allowed_action, safe_gesture


def main():
    parser = argparse.ArgumentParser(description='Gesture Control v0.2.2')
    parser.add_argument('--config', default='config.toml')
    parser.add_argument('--source', help='URL MJPEG do tablet ou indice da webcam')
    parser.add_argument('--preview', action='store_true', help='Janela de diagnostico: A alterna, Q sai')
    parser.add_argument('--arm', action='store_true', help='Ativa interpretacao de gestos sem janela')
    parser.add_argument('--live', action='store_true', help='Executa comandos reais: abrir/maximizar')
    parser.add_argument('--allow-close', action='store_true', help='Opt-in para fechamento real')
    parser.add_argument('--allow-move', action='store_true', help='Opt-in para arrastar janelas reais')
    args = parser.parse_args()
    if (args.allow_close or args.allow_move) and not args.live:
        parser.error('--allow-close/--allow-move exigem --live')
    if args.live and not (args.arm or args.preview):
        parser.error('--live exige --arm ou --preview para ativacao explicita')
    cfg = Config.load(args.config)
    source = args.source or cfg.source
    if not Path(cfg.model).is_file():
        parser.error(f'Modelo ausente: {cfg.model}')

    backend = Hyprland(live=args.live, command=cfg.open_command)
    logic = GestureLogic(cfg.dwell_seconds, cfg.cooldown_seconds, cfg.move_scale, close_dwell=2.5)
    selector = HandSelector()
    armed = bool(args.arm)
    tracker = HandTracker(cfg.model, num_hands=2)
    failures = 0
    hand_missing = False
    mode = 'REAL: ABRIR/MAXIMIZAR' if args.live else 'SIMULACAO'
    print(f'Gesture Control v0.2.2 | {mode}')
    print(f'Fechar real: {args.live and args.allow_close} | Mover real: {args.live and args.allow_move}')
    print(f'Diagnostico: {args.preview} | Controle armado: {armed}')
    print('Encerrar: Ctrl+C' + (' ou Q na janela' if args.preview else ''))
    try:
        with Camera(source, cfg.mirror) as camera:
            while True:
                frame = camera.read()
                if frame is None:
                    failures += 1
                    if not hand_missing:
                        logic.suspend()
                        hand_missing = True
                    selector.reset()
                    backend.drag_target = None
                    if failures >= 15:
                        raise RuntimeError('Fluxo de video interrompido')
                    time.sleep(.08)
                    continue
                failures = 0
                hands = tracker.detect(frame)
                selected = selector.select(hands)
                gesture = classify(selected) if selected is not None else Gesture('none')
                if selected is None:
                    if not hand_missing:
                        logic.suspend()
                        hand_missing = True
                    backend.drag_target = None
                else:
                    hand_missing = False
                # Uma pinça sem permissão de movimento não altera o estado do arraste.
                effective = safe_gesture(gesture, move_enabled=(not args.live or args.allow_move))
                # Mesmo sem mão, a ausência estável deve liberar o próximo gesto.
                if armed:
                    action = logic.update(effective, time.monotonic())
                    if action:
                        if allowed_action(action, args.live, args.allow_close, args.allow_move):
                            print(f'[{mode}] gesto={gesture.name} acao={action}', flush=True)
                            try:
                                backend.handle(action)
                            except Exception as error:
                                print(f'Erro no comando: {error}', flush=True)
                                logic.reset()
                                backend.drag_target = None
                        else:
                            print(f'[BLOQUEADO] {action.name}: habilitacao explicita necessaria', flush=True)
                if args.preview:
                    draw_debug(frame, hands, gesture.name, armed)
                    cv2.imshow('Gesture Control - Diagnostico', frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    if key == ord('a'):
                        armed = not armed
                        logic.reset()
                        selector.reset()
                        backend.drag_target = None
                        print('Armado' if armed else 'Desarmado', flush=True)
    except KeyboardInterrupt:
        print('\nEncerrado pelo usuario.')
    finally:
        tracker.close()
        if args.preview:
            cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
