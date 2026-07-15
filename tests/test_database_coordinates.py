import unittest

from database import _has_coordinate_value


class DatabaseCoordinateValueTests(unittest.TestCase):
    def test_zero_is_allowed_as_coordinate(self):
        self.assertTrue(_has_coordinate_value(0))
        self.assertTrue(_has_coordinate_value(0.0))

    def test_empty_string_is_rejected(self):
        self.assertFalse(_has_coordinate_value(""))
        self.assertFalse(_has_coordinate_value(None))


if __name__ == "__main__":
    unittest.main()
