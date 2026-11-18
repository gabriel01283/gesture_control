import unittest
from gesture_control.gestures import Gesture
from gesture_control.logic import GestureLogic, Action
from gesture_control.policy import safe_gesture


class AbsenceAndPolicyTests(unittest.TestCase):
    def test_absence_releases_after_suspension(self):
        logic = GestureLogic(dwell=0.6, cooldown=0.8, release_seconds=0.4)
        logic.suspend()
        self.assertIsNone(logic.update(Gesture('none'), 0.0))
        self.assertIsNone(logic.update(Gesture('none'), 0.5))
        self.assertIsNone(logic.update(Gesture('victory'), 1.0))
        self.assertEqual(logic.update(Gesture('victory'), 1.7), Action('open'))

    def test_disallowed_pinch_does_not_start_drag(self):
        logic = GestureLogic(dwell=0.6)
        gesture = safe_gesture(Gesture('pinch', .3, .4), move_enabled=False)
        self.assertEqual(gesture.name, 'neutral')
        self.assertIsNone(logic.update(gesture, 0.0))

    def test_allowed_pinch_preserved(self):
        self.assertEqual(safe_gesture(Gesture('pinch'), move_enabled=True).name, 'pinch')


if __name__ == '__main__':
    unittest.main()
