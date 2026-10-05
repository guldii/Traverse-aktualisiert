import unittest
from traverse_lochabstand import calculate


class CalculationTests(unittest.TestCase):
    def test_exact_multiple(self):
        r = calculate(2000, 50, 50, 190)
        self.assertEqual(r.intervals, 10)
        self.assertEqual(r.holes, 11)
        self.assertAlmostEqual(r.spacing, 190)

    def test_lower_candidate_selected(self):
        # Nutzstrecke 1000; Kandidaten n=3 (333.33) und n=4 (250).
        # Bei Soll 300 ist die Abweichung für n=3 kleiner.
        r = calculate(1100, 50, 50, 300)
        self.assertEqual(r.intervals, 3)

    def test_upper_candidate_selected(self):
        # Nutzstrecke 1000; bei Soll 270 liegt n=4 (250) näher als n=3.
        r = calculate(1100, 50, 50, 270)
        self.assertEqual(r.intervals, 4)

    def test_tie_prefers_larger_spacing(self):
        # Nutzstrecke 120; Soll 55: n=2 => 60 (Fehler 5), n=3 => 40
        # (Fehler 15), damit kein Gleichstand. Echter Gleichstand:
        # Strecke 100, Soll 40: n=2 => 50, n=3 => 33.333, kein exakter tie.
        # Verwenden Sie symmetrische Werte: Strecke 12, Soll 5.5,
        # n=2 => 6 (0.5), n=3 => 4 (1.5), ebenfalls nicht gleich.
        # Test tie construction via candidates where L/n distances straddle s.
        # L=12, n=2 gives 6, n=3 gives 4; midpoint target 5 gives equal errors.
        r = calculate(12, 0, 0, 5)
        self.assertEqual(r.intervals, 2)
        self.assertAlmostEqual(r.spacing, 6)

    def test_many_holes(self):
        r = calculate(10000, 10, 10, 2)
        self.assertGreater(r.holes, 4000)

    def test_fastening_holes_are_two(self):
        r = calculate(1000, 50, 50, 100)
        self.assertEqual(r.fastening_holes, 2)
        self.assertEqual(r.holes_without_fastening, r.holes - 2)

    def test_invalid_values(self):
        for args in [(0, 0, 0, 10), (100, -1, 0, 10), (100, 0, 0, 0),
                     (100, 50, 50, 10)]:
            with self.assertRaises(ValueError):
                calculate(*args)

    def test_tiny_spacing(self):
        r = calculate(10, 0, 0, 0.001)
        self.assertGreater(r.holes, 1000)

    def test_start_end_accounted(self):
        r = calculate(2000, 50, 50, 190)
        self.assertAlmostEqual(r.usable, 1900)
        self.assertAlmostEqual(r.start + r.usable + r.end, r.length)

    def test_round_only_for_display(self):
        r = calculate(1000, 0.123456, 0.234567, 100)
        self.assertNotEqual(r.usable, round(r.usable, 2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
