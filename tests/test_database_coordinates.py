import unittest

from database import _has_coordinate_value, _validate_non_negative_length_value


class DatabaseCoordinateValueTests(unittest.TestCase):
    def test_zero_is_allowed_as_coordinate(self):
        self.assertTrue(_has_coordinate_value(0))
        self.assertTrue(_has_coordinate_value(0.0))

    def test_empty_string_is_rejected(self):
        self.assertFalse(_has_coordinate_value(""))
        self.assertFalse(_has_coordinate_value(None))

    def test_zero_is_allowed_for_rectangle_length(self):
        self.assertTrue(_validate_non_negative_length_value("0"))
        self.assertTrue(_validate_non_negative_length_value(0.0))

    def test_negative_value_is_rejected_for_rectangle_length(self):
        self.assertFalse(_validate_non_negative_length_value("-1"))
        self.assertFalse(_validate_non_negative_length_value(-2.5))


if __name__ == "__main__":
    unittest.main()
