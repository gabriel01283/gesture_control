import unittest
from unittest.mock import patch
from gesture_control.hyprland import Hyprland
from gesture_control.logic import Action


class HyprlandLuaTests(unittest.TestCase):
    def test_dry_run_never_calls_subprocess(self):
        with patch('subprocess.run', side_effect=AssertionError('chamada real')):
            h = Hyprland()
            for name in ('open', 'maximize', 'close', 'drag_start', 'drag_move', 'drag_stop'):
                h.handle(Action(name, 15, 20))

    def test_lua_open(self):
        with patch.object(Hyprland, 'run', return_value='ok') as run:
            Hyprland().handle(Action('open'))
        args = run.call_args.args
        self.assertEqual(args[:2], ('hyprctl', 'eval'))
        self.assertIn('hl.dsp.exec_cmd("kitty")', args[2])

    def test_lua_maximize_and_close(self):
        with patch.object(Hyprland, 'run', return_value='ok') as run:
            h = Hyprland()
            h.handle(Action('maximize'))
            self.assertIn('mode = "maximized"', run.call_args.args[2])
            self.assertIn('address:0xDEADBEEF', run.call_args.args[2])
            h.handle(Action('close'))
            self.assertIn('hl.dsp.window.close', run.call_args.args[2])
            self.assertNotIn('kill', run.call_args.args[2])

    def test_drag_requires_floating_and_clamps(self):
        with patch.object(Hyprland, 'run', return_value='ok') as run:
            h = Hyprland()
            h.handle(Action('drag_start'))
            h.handle(Action('drag_move', 900, -900))
            self.assertIn('x = 150, y = -150', run.call_args.args[2])
            h.handle(Action('drag_stop'))
            self.assertIsNone(h.drag_target)

    def test_invalid_address_rejected(self):
        with self.assertRaises(ValueError):
            Hyprland._window_ref('oops');

if __name__ == '__main__':
    unittest.main()
