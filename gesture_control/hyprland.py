"""Adaptador isolado do Hyprland 0.57 (Lua). Simulacao e o padrao.

Nao faz chamadas reais sem live=True. O processo principal v0.2 ainda bloqueia
modo real ate que o sistema de seguranca de gestos seja validado.
"""
import json
import re
import shlex
import subprocess
from .logic import Action

_ADDRESS = re.compile(r"0x[0-9a-fA-F]+\Z")


class Hyprland:
    def __init__(self, live=False, command='kitty', api='lua'):
        if api != 'lua':
            raise ValueError('Apenas a API Lua do Hyprland 0.57 e suportada')
        self.live = live
        self.command = shlex.split(command)
        if not self.command:
            raise ValueError('Comando de abertura vazio')
        self.drag_target = None

    def run(self, *args):
        if not self.live:
            print('[SIMULAÇÃO]', ' '.join(args))
            return ''
        result = subprocess.run(args, capture_output=True, text=True,
                                timeout=3, check=True)
        if 'error' in result.stdout.lower() and result.stdout.strip() != 'ok':
            raise RuntimeError(result.stdout.strip())
        return result.stdout

    def active(self):
        if not self.live:
            return {'address': '0xDEADBEEF', 'floating': True, 'class': 'demo'}
        result = subprocess.run(['hyprctl', '-j', 'activewindow'],
                                capture_output=True, text=True, timeout=3, check=True)
        data = json.loads(result.stdout)
        if not data or not data.get('address'):
            return None
        return data

    @staticmethod
    def _window_ref(address):
        if not isinstance(address, str) or not _ADDRESS.fullmatch(address):
            raise ValueError('Endereco da janela invalido')
        return json.dumps('address:' + address)

    def dispatch(self, expression):
        # Exige expressao preparada internamente, nunca entrada da camera.
        return self.run('hyprctl', 'eval', f'hl.dispatch({expression})')

    def handle(self, action: Action):
        if action.name == 'open':
            cmd = json.dumps(shlex.join(self.command))
            self.dispatch(f'hl.dsp.exec_cmd({cmd})')
        elif action.name in ('close', 'maximize'):
            win = self.active()
            if not win:
                return
            ref = self._window_ref(win['address'])
            if action.name == 'close':
                # Fechamento gracioso, nao SIGKILL.
                self.dispatch(f'hl.dsp.window.close({{ window = {ref} }})')
            else:
                self.dispatch('hl.dsp.window.fullscreen('
                              f'{{ window = {ref}, mode = "maximized", action = "toggle" }})')
        elif action.name == 'drag_start':
            win = self.active()
            self.drag_target = (win['address'] if win and win.get('floating') else None)
            if self.drag_target:
                self._window_ref(self.drag_target)
            else:
                print('Mover exige janela flutuante ativa')
        elif action.name == 'drag_move' and self.drag_target:
            ref = self._window_ref(self.drag_target)
            dx, dy = int(action.dx), int(action.dy)
            # Limite por evento para minimizar deslocamentos inesperados.
            dx = max(-150, min(150, dx))
            dy = max(-150, min(150, dy))
            if dx or dy:
                self.dispatch('hl.dsp.window.move('
                              f'{{ window = {ref}, x = {dx}, y = {dy}, relative = true }})')
        elif action.name == 'drag_stop':
            self.drag_target = None
