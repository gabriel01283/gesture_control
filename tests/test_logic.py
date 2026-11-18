import unittest
from gesture_control.logic import GestureLogic, Action
from gesture_control.gestures import Gesture
from gesture_control.hyprland import Hyprland

class LogicTests(unittest.TestCase):
    def test_requires_sustained_gesture(self):
        l = GestureLogic(dwell=1.0)
        self.assertIsNone(l.update(Gesture('victory'), 0))
        self.assertIsNone(l.update(Gesture('victory'), .5))
        self.assertEqual(l.update(Gesture('victory'), 1.1), Action('open'))
        self.assertIsNone(l.update(Gesture('victory'), 1.2))
        self.assertIsNone(l.update(Gesture('victory'), 5.0))

    def test_lost_hand_resets_candidate(self):
        l = GestureLogic(dwell=1.0)
        l.update(Gesture('fist'), 0)
        l.update(Gesture('none'), .6)
        self.assertIsNone(l.update(Gesture('fist'), 1.1))
        self.assertEqual(l.update(Gesture('fist'), 2.2), Action('close'))

    def test_drag_lifecycle(self):
        l = GestureLogic()
        self.assertEqual(l.update(Gesture('pinch', .2, .3), 0), Action('drag_start'))
        self.assertEqual(l.update(Gesture('pinch', .3, .3), .2), Action('drag_move', 120, 0))
        self.assertEqual(l.update(Gesture('none'), .4), Action('drag_stop'))

    def test_dry_run_does_not_invoke_hyprctl(self):
        h = Hyprland()
        for action in ('open','maximize','close','drag_start','drag_move','drag_stop'):
            h.handle(Action(action, 30, 40))

if __name__ == '__main__':
    unittest.main()
