import unittest
from day1 import part1_elems, part2_elems

class TestDay(unittest.TestCase):

    # Part 1

    def test_part1_example1(self):
        self.assertEqual(3, part1_elems([+1, -2, +3, +1]))

    def test_part1_example2(self):
        self.assertEqual(3, part1_elems([+1, +1, +1]))

    def test_part1_example3(self):
        self.assertEqual(0, part1_elems([+1, +1, -2]))

    def test_part1_example4(self):
        self.assertEqual(-6, part1_elems([-1, -2, -3]))

    # Part 2

    def test_part2_example1(self):
        self.assertEqual(2, part2_elems([+1, -2, +3, +1]))

    def test_part2_example2(self):
        self.assertEqual(0, part2_elems([+1, -1]))

    def test_part2_example3(self):
        self.assertEqual(10, part2_elems([+3, +3, +4, -2, -4]))

    def test_part2_example4(self):
        self.assertEqual(5, part2_elems([-6, +3, +8, +5, -6]))

    def test_part2_example5(self):
        self.assertEqual(14, part2_elems([+7, +7, -2, -7, -4]))

if __name__ == '__main__':
    unittest.main()


