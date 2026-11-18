"""Adaptador Hyprland. Backend legado é opt-in; dry-run é padrão."""
import json
import re
import shlex
import subprocess
from .logic import Action

class Hyprland:
    def __init__(self, live=False, command='kitty', api='legacy'):
        self.live = live
        self.command = shlex.split(command)
        self.api = api
        self.drag_target = None
        if not self.command:
            raise ValueError('Comando de abertura vazio')

    def run(self, *args):
        if not self.live:
            print('[SIMULAÇÃO]', ' '.join(args))
            return ''
        result = subprocess.run(args, capture_output=True, text=True, timeout=3, check=True)
        return result.stdout

    def active(self):
        if not self.live:
            return {'address': '0xSIMULADO', 'floating': True, 'class': 'demo'}
        data = json.loads(self.run('hyprctl', '-j', 'activewindow'))
        if not data or not data.get('address'):
            return None
        return data

    def dispatch(self, name, argument=None):
        if self.api != 'legacy':
            raise RuntimeError('Backend não suportado: configure um adaptador da versão instalada')
        args = ['hyprctl', 'dispatch', name]
        if argument is not None:
            args.append(str(argument))
        self.run(*args)

    def handle(self, action: Action):
        if action.name == 'open':
            # Execução permitida somente para o comando configurado localmente.
            self.dispatch('exec', shlex.join(self.command))
        elif action.name in ('close', 'maximize'):
            win = self.active()
            if not win:
                print('Nenhuma janela ativa')
                return
            # Não fecha o processo à força; solicita encerramento normal.
            addr = win['address']
            if not re.fullmatch(r'0x[0-9a-fA-F]+', addr) and self.live:
                raise ValueError('Endereço de janela inválido')
            if action.name == 'close':
                self.dispatch('closewindow', f'address:{addr}')
            else:
                # 1 significa maximizar (não fullscreen exclusivo).
                self.dispatch('fullscreen', '1')
        elif action.name == 'drag_start':
            win = self.active()
            self.drag_target = win['address'] if win and win.get('floating') else None
            if not self.drag_target:
                print('Mover exige janela flutuante ativa; nenhuma janela selecionada')
        elif action.name == 'drag_move' and self.drag_target:
            if not re.fullmatch(r'0x[0-9a-fA-F]+', self.drag_target) and self.live:
                return
            self.dispatch('movewindowpixel', f'{action.dx} {action.dy},address:{self.drag_target}')
        elif action.name == 'drag_stop':
            self.drag_target = None
