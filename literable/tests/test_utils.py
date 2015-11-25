import unittest
from literable import utils


class TimeStringParserTest(unittest.TestCase):
    def test_parsing_one_digit_minute(self):
        self.assertEqual(3, utils.parse_duration_string("3m"))

    def test_parsing_3_digit_minute(self):
        self.assertEqual(82, utils.parse_duration_string("82m"))

    def test_parsing_one_digit_hour(self):
        self.assertEqual(180, utils.parse_duration_string("3h"))

    def test_parsing_3_digit_hour(self):
        self.assertEqual(7380, utils.parse_duration_string("123h"))

    def test_parsing_one_digit_day(self):
        self.assertEqual(4320, utils.parse_duration_string("3d"))

    def test_parsing_3_digit_day(self):
        self.assertEqual(177120, utils.parse_duration_string("123d"))

    def test_parsing_one_digit_week(self):
        self.assertEqual(30240, utils.parse_duration_string("3w"))

    def test_parsing_3_digit_week(self):
        self.assertEqual(1239840, utils.parse_duration_string("123w"))

    def test_all_together(self):
        self.assertEqual(24752, utils.parse_duration_string("2w 3d 4h 32m"))

    def test_all_together_unordered(self):
        self.assertEqual(15924, utils.parse_duration_string("1h 24m 1w 4d"))

    def test_zero(self):
        self.assertEqual(0, utils.parse_duration_string("0h 0m"))

    def test_doesnt_start_with_number(self):
        with self.assertRaises(SyntaxError):
            utils.parse_duration_string("1h m2")

    def test_doesnt_have_time_unit(self):
        with self.assertRaises(SyntaxError):
            utils.parse_duration_string("1d 2 4m")


class TimeStringFormatterTest(unittest.TestCase):
    def test_formatting_one(self):
        self.assertEqual("2h", utils.format_duration(120))

    def test_formatting_multi(self):
        self.assertEqual("2w 3d 4h 32m", utils.format_duration(24752))


if __name__ == '__main__':
    unittest.main()