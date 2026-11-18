import unittest
from types import SimpleNamespace
from gesture_control.selection import select_control_hand


class SelectionTests(unittest.TestCase):
    def test_no_hand(self):
        self.assertIsNone(select_control_hand([]))
        self.assertIsNone(select_control_hand(None))

    def test_one_hand(self):
        hand = [SimpleNamespace(x=0.3)] * 21
        self.assertIs(select_control_hand([hand]), hand)

    def test_selects_rightmost_in_mirrored_image(self):
        left = [SimpleNamespace(x=0.2)] * 21
        right = [SimpleNamespace(x=0.8)] * 21
        self.assertIs(select_control_hand([left, right]), right)
        self.assertIs(select_control_hand([right, left]), right)


if __name__ == '__main__':
    unittest.main()
