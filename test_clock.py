#!/usr/bin/env python3
"""
Test suite for the Bernese German word clock.
Run without any hardware to verify the time-to-words logic.
"""

import unittest
from word_grid import get_words_for_time, get_minute_dots, HOUR_WORDS, WORDS


class TestWordClock(unittest.TestCase):
    """Test the word clock time logic."""

    def test_on_the_hour(self):
        """Test times exactly on the hour."""
        # 7:00 → ES ISCH SIBNI UHR
        words = get_words_for_time(7, 0)
        self.assertIn("ES", words)
        self.assertIn("ISCH", words)
        self.assertIn("SIBNI", words)
        self.assertIn("UHR", words)
        self.assertNotIn("AB", words)
        self.assertNotIn("VOR", words)

    def test_five_past(self):
        """Test 5 minutes past the hour."""
        # 7:05 → ES ISCH FÜF AB SIBNI
        words = get_words_for_time(7, 5)
        self.assertIn("FÜF", words)
        self.assertIn("AB", words)
        self.assertIn("SIBNI", words)
        self.assertNotIn("UHR", words)

    def test_ten_past(self):
        """Test 10 minutes past the hour."""
        # 7:10 → ES ISCH ZÄÄ AB SIBNI
        words = get_words_for_time(7, 10)
        self.assertIn("ZÄÄ", words)
        self.assertIn("AB", words)
        self.assertIn("SIBNI", words)

    def test_quarter_past(self):
        """Test quarter past the hour."""
        # 7:15 → ES ISCH VIERT AB SIBNI
        words = get_words_for_time(7, 15)
        self.assertIn("VIERT", words)
        self.assertIn("AB", words)
        self.assertIn("SIBNI", words)

    def test_twenty_past(self):
        """Test 20 minutes past the hour."""
        # 7:20 → ES ISCH ZWÄNZG AB SIBNI
        words = get_words_for_time(7, 20)
        self.assertIn("ZWÄNZG", words)
        self.assertIn("AB", words)
        self.assertIn("SIBNI", words)

    def test_five_to_half(self):
        """Test 25 minutes past (5 before half)."""
        # 7:25 → ES ISCH FÜF VOR HAUBI ACHTI
        words = get_words_for_time(7, 25)
        self.assertIn("FÜF", words)
        self.assertIn("VOR", words)
        self.assertIn("HAUBI", words)
        self.assertIn("ACHTI", words)  # Next hour

    def test_half(self):
        """Test half past the hour."""
        # 7:30 → ES ISCH HAUBI ACHTI
        words = get_words_for_time(7, 30)
        self.assertIn("HAUBI", words)
        self.assertIn("ACHTI", words)
        self.assertNotIn("AB", words)
        self.assertNotIn("VOR", words)

    def test_five_past_half(self):
        """Test 35 minutes past (5 past half)."""
        # 7:35 → ES ISCH FÜF AB HAUBI ACHTI
        words = get_words_for_time(7, 35)
        self.assertIn("FÜF", words)
        self.assertIn("AB", words)
        self.assertIn("HAUBI", words)
        self.assertIn("ACHTI", words)

    def test_twenty_to(self):
        """Test 20 minutes to the hour."""
        # 7:40 → ES ISCH ZWÄNZG VOR ACHTI
        words = get_words_for_time(7, 40)
        self.assertIn("ZWÄNZG", words)
        self.assertIn("VOR", words)
        self.assertIn("ACHTI", words)

    def test_quarter_to(self):
        """Test quarter to the hour."""
        # 7:45 → ES ISCH VIERT VOR ACHTI
        words = get_words_for_time(7, 45)
        self.assertIn("VIERT", words)
        self.assertIn("VOR", words)
        self.assertIn("ACHTI", words)

    def test_ten_to(self):
        """Test 10 minutes to the hour."""
        # 7:50 → ES ISCH ZÄÄ VOR ACHTI
        words = get_words_for_time(7, 50)
        self.assertIn("ZÄÄ", words)
        self.assertIn("VOR", words)
        self.assertIn("ACHTI", words)

    def test_five_to(self):
        """Test 5 minutes to the hour."""
        # 7:55 → ES ISCH FÜF VOR ACHTI
        words = get_words_for_time(7, 55)
        self.assertIn("FÜF", words)
        self.assertIn("VOR", words)
        self.assertIn("ACHTI", words)

    def test_midnight(self):
        """Test midnight (00:00)."""
        words = get_words_for_time(0, 0)
        self.assertIn("ZWÖUFI", words)
        self.assertIn("UHR", words)

    def test_noon(self):
        """Test noon (12:00)."""
        words = get_words_for_time(12, 0)
        self.assertIn("ZWÖUFI", words)
        self.assertIn("UHR", words)

    def test_24h_conversion(self):
        """Test 24-hour to 12-hour conversion."""
        # 14:00 → ES ISCH ZWÖI UHR
        words = get_words_for_time(14, 0)
        self.assertIn("ZWÖI", words)

        # 23:00 → ES ISCH ÖUFI UHR
        words = get_words_for_time(23, 0)
        self.assertIn("ÖUFI", words)

    def test_minute_dots_0(self):
        """Test minute dots for exact 5-minute intervals."""
        self.assertEqual(get_minute_dots(0), 0)
        self.assertEqual(get_minute_dots(5), 0)
        self.assertEqual(get_minute_dots(10), 0)
        self.assertEqual(get_minute_dots(55), 0)

    def test_minute_dots_1_to_4(self):
        """Test minute dots for in-between minutes."""
        self.assertEqual(get_minute_dots(1), 1)
        self.assertEqual(get_minute_dots(2), 2)
        self.assertEqual(get_minute_dots(3), 3)
        self.assertEqual(get_minute_dots(4), 4)
        self.assertEqual(get_minute_dots(6), 1)
        self.assertEqual(get_minute_dots(47), 2)
        self.assertEqual(get_minute_dots(59), 4)

    def test_all_hours_exist(self):
        """Test that all hour words are defined."""
        for hour in range(1, 13):
            self.assertIn(hour, HOUR_WORDS)
            word = HOUR_WORDS[hour]
            self.assertIn(word, WORDS)

    def test_es_isch_always_present(self):
        """Test that ES ISCH is always in the output."""
        for hour in range(24):
            for minute in range(60):
                words = get_words_for_time(hour, minute)
                self.assertIn("ES", words, f"ES missing at {hour}:{minute}")
                self.assertIn("ISCH", words, f"ISCH missing at {hour}:{minute}")


class TestWordGrid(unittest.TestCase):
    """Test the word grid layout."""

    def test_grid_dimensions(self):
        """Test that the grid has correct dimensions."""
        from word_grid import GRID
        self.assertEqual(len(GRID), 10)  # 10 rows
        for row in GRID:
            self.assertEqual(len(row), 11)  # 11 columns

    def test_word_positions_valid(self):
        """Test that all word positions are within grid bounds."""
        from word_grid import WORDS, GRID
        for word, (row, start, end) in WORDS.items():
            self.assertLess(row, len(GRID), f"Row out of bounds for {word}")
            self.assertLessEqual(end, len(GRID[row]) - 1, f"Column out of bounds for {word}")
            self.assertLessEqual(start, end, f"Invalid range for {word}")

    def test_word_extraction(self):
        """Test that words can be extracted from their positions."""
        from word_grid import WORDS, GRID

        for word, (row, start, end) in WORDS.items():
            extracted = GRID[row][start:end + 1]
            self.assertEqual(extracted, word, f"Word {word} doesn't match grid at ({row}, {start}-{end})")


def run_visual_demo():
    """Run a visual demonstration of all times."""
    from word_grid import print_time_display

    print("\n" + "=" * 50)
    print("  VISUAL DEMO - All 12 time intervals")
    print("=" * 50)

    demo_times = [
        (10, 0, "on the hour"),
        (10, 7, "5 past + 2 dots"),
        (10, 10, "10 past"),
        (10, 15, "quarter past"),
        (10, 20, "20 past"),
        (10, 25, "5 to half"),
        (10, 30, "half"),
        (10, 35, "5 past half"),
        (10, 40, "20 to"),
        (10, 45, "quarter to"),
        (10, 50, "10 to"),
        (10, 55, "5 to"),
    ]

    for hour, minute, desc in demo_times:
        print(f"\n--- {desc} ---")
        print_time_display(hour, minute)


if __name__ == "__main__":
    import sys

    if "--demo" in sys.argv:
        run_visual_demo()
    else:
        # Run tests
        unittest.main(verbosity=2)
