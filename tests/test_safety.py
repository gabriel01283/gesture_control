import unittest
from types import SimpleNamespace
from gesture_control.logic import GestureLogic, Action
from gesture_control.gestures import Gesture
from gesture_control.selection import HandSelector
from gesture_control.policy import allowed_action


def hand(x, y=.5):
    return [SimpleNamespace(x=x, y=y)] * 21


class SafetyTests(unittest.TestCase):
    def test_no_repeat_without_release(self):
        l = GestureLogic(dwell=.5, cooldown=0, release_seconds=.4)
        self.assertIsNone(l.update(Gesture('open_palm'), 0))
        self.assertEqual(l.update(Gesture('open_palm'), .6), Action('maximize'))
        for t, gesture in [(.7, 'neutral'), (.8, 'open_palm'), (1.5, 'open_palm'), (5, 'open_palm')]:
            self.assertIsNone(l.update(Gesture(gesture), t))

    def test_release_then_repeat(self):
        l = GestureLogic(dwell=.5, cooldown=0, release_seconds=.4)
        l.update(Gesture('victory'), 0)
        self.assertEqual(l.update(Gesture('victory'), .6), Action('open'))
        l.update(Gesture('neutral'), .7)
        l.update(Gesture('neutral'), 1.2)
        self.assertIsNone(l.update(Gesture('victory'), 1.3))
        self.assertEqual(l.update(Gesture('victory'), 1.9), Action('open'))

    def test_close_requires_long_hold(self):
        l = GestureLogic(dwell=.5, cooldown=0, close_dwell=2.5)
        l.update(Gesture('fist'), 0)
        self.assertIsNone(l.update(Gesture('fist'), 1.5))
        self.assertEqual(l.update(Gesture('fist'), 2.6), Action('close'))

    def test_live_blocks_close_and_drag(self):
        self.assertTrue(allowed_action(Action('open'), live=True))
        self.assertTrue(allowed_action(Action('maximize'), live=True))
        self.assertFalse(allowed_action(Action('close'), live=True))
        self.assertFalse(allowed_action(Action('drag_start'), live=True))
        self.assertTrue(allowed_action(Action('close'), live=True, allow_close=True))
        self.assertTrue(allowed_action(Action('drag_move'), live=True, allow_move=True))

    def test_selection_stable_when_order_changes(self):
        selector = HandSelector()
        left, right = hand(.2), hand(.8)
        self.assertIs(selector.select([left, right]), right)
        right2 = hand(.78)
        self.assertIs(selector.select([right2, left]), right2)
        self.assertIsNone(selector.select([]))
        self.assertIsNone(selector.select([left]))

    def test_selection_rejects_jump(self):
        selector = HandSelector()
        self.assertIsNotNone(selector.select([hand(.8)]))
        self.assertIsNone(selector.select([hand(.1)]))


if __name__ == '__main__':
    unittest.main()
