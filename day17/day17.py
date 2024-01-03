import collections
import re

Line = collections.namedtuple('Line', 'min_x max_x min_y max_y')

range_regexp = re.compile(r'\s*(?P<axis>[x|y])=(?P<min>\d+)(\.\.(?P<max>\d+))?\s*')

sand_and_then_clay = re.compile(r'(\.)*#')


class Ground:

    def __init__(self, lines):
        self.parsed_lines = [parse_line(line) for line in lines]
        self._get_limits()
        self._create_slice()
        self._fill_with_clay()
        self._create_spring()

    def _get_limits(self):
        self.min_x = min(l.min_x for l in self.parsed_lines) - 1
        self.max_x = max(l.max_x for l in self.parsed_lines) + 1
        self.real_min_y = min(l.min_y for l in self.parsed_lines)
        self.min_y = min(self.real_min_y, 0)
        self.max_y = max(l.max_y for l in self.parsed_lines)
        self.width = self.max_x - self.min_x + 1
        self.height = self.max_y - self.min_y + 1

    def _create_slice(self):
        self.slice = [['.' for _ in range(self.width)] for _ in range(self.height)]

    def _fill_with_clay(self):
        for min_x, max_x, min_y, max_y in self.parsed_lines:
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    self.set(x, y, '#')

    def _create_spring(self):
        self.set(500, 0, '+')
        self.drops = [(500, 0)]

    def get(self, x, y):
        return self.slice[y - self.min_y][x - self.min_x]

    def set(self, x, y, val):
        self.slice[y - self.min_y][x - self.min_x] = val

    def show(self):
        return '\n'.join(''.join(self.get(x, y)
                                 for x in range(self.min_x, self.max_x + 1))
                         for y in range(self.min_y, self.max_y + 1))

    def find_bottom(self, x, y, bottom):
        xx_min = x
        while self.get(xx_min - 1, y) == bottom:
            xx_min -= 1
        xx_max = x
        while self.get(xx_max + 1, y) == bottom:
            xx_max += 1
        return xx_min, xx_max

    def find_sand(self, x, y):
        xx_min = x
        while xx_min > self.min_x + 1 and self.get(xx_min - 1, y) == '.':
            xx_min -= 1
        xx_max = x
        while xx_max < self.max_x - 1 and self.get(xx_max + 1, y) == '.':
            xx_max += 1
        if self.get(xx_min - 1, y) == '#' and self.get(xx_max + 1, y) == '#':
            return xx_min, xx_max
        else:
            return None

    def steps(self):
        while True:
            if len(self.drops) == 0:
                return

            (x, y) = self.drops.pop()

            if y == self.max_y:
                continue

            if self.get(x, y) == '+':
                if self.get(x, y + 1) == '.':
                    self.set(x, y + 1, '|')
                    yield
                    self.drops.append((x, y + 1))
            elif self.get(x, y) == '|':
                if self.get(x, y + 1) == '.':
                    self.set(x, y + 1, '|')
                    yield
                    self.drops.append((x, y))
                    self.drops.append((x, y + 1))
                elif self.get(x, y + 1) in ('#', '~'):
                    if self.get(x - 1, y) == '.':
                        self.set(x - 1, y, '|')
                        yield
                        self.drops.append((x - 1, y))
                    elif self.get(x - 1, y) == '#' and self.get(x,y) == '|':
                        right = self.find_right(x, y, '|')
                        if right:
                            self.rest_water(x, right, y)
                            yield

                    if self.get(x + 1, y) == '.':
                        self.set(x + 1, y, '|')
                        yield
                        self.drops.append((x + 1, y))
                    elif self.get(x + 1, y) == '#' and self.get(x,y) == '|':
                        left = self.find_left(x, y, '|')
                        if left:
                            self.rest_water(left, x, y)
                            yield

    def run(self, debug=False):
        if debug:
            self.print()
        for _ in self.steps():
            if debug:
                self.print()

    def print(self):
        print()
        print(self.show())

    def count(self):
        return sum(1 for row in self.slice for c in row if c in ('|', '~'))

    def count_dry(self):
        return sum(1 for row in self.slice for c in row if c == '~')

    def find_right(self, x, y, char):
        assert self.get(x, y) == char
        assert self.get(x, y + 1) in ('#', '~')
        x_max = x
        while self.get(x_max + 1, y) == char and self.get(x_max + 1, y + 1) in ('#', '~'):
            x_max += 1
        if self.get(x_max + 1, y) == '#' and self.get(x_max + 1, y + 1) in ('#', '~'):
            return x_max
        else:
            return None

    def find_left(self, x, y, char):
        assert self.get(x, y) == char
        assert self.get(x, y + 1) in ('#', '~')
        x_min = x
        while self.get(x_min - 1, y) == char and self.get(x_min - 1, y + 1) in ('#', '~'):
            x_min -= 1
        if self.get(x_min - 1, y) == '#' and self.get(x_min - 1, y + 1) in ('#', '~'):
            return x_min
        else:
            return None

    def rest_water(self, x_min, x_max, y):
        for x in range(x_min, x_max + 1):
            self.set(x, y, '~')


def parse_line(line):
    limits = [0] * 4
    for part in line.split(','):
        groups = range_regexp.match(part).groupdict()
        offset = 0 if groups['axis'] == 'x' else 2
        min_ = int(groups['min'])
        max_ = int(groups['max']) if groups['max'] else min_
        limits[offset] = min_
        limits[offset + 1] = max_
    return Line(*limits)


def test_parse_line():
    assert Line(495, 495, 2, 7) == parse_line('x=495, y=2..7')
    assert Line(495, 501, 7, 7) == parse_line('y=7, x=495..501')
    assert Line(501, 501, 3, 7) == parse_line('x=501, y=3..7')
    assert Line(498, 498, 2, 4) == parse_line('x=498, y=2..4')
    assert Line(506, 506, 1, 2) == parse_line('x=506, y=1..2')
    assert Line(498, 498, 10, 13) == parse_line('x=498, y=10..13')
    assert Line(504, 504, 10, 13) == parse_line('x=504, y=10..13')
    assert Line(498, 504, 13, 13) == parse_line('y=13, x=498..504')


def test_show():
    expected = """\
......+.......
............#.
.#..#.......#.
.#..#..#......
.#..#..#......
.#.....#......
.#.....#......
.#######......
..............
..............
....#.....#...
....#.....#...
....#.....#...
....#######..."""

    with open('test_input.txt', 'r') as test:
        test_ground = Ground(line.strip() for line in test)
        assert expected == test_ground.show()


def test_run():
    expected = """\
......+.......
......|.....#.
.#..#||||...#.
.#..#~~#|.....
.#..#~~#|.....
.#~~~~~#|.....
.#~~~~~#|.....
.#######|.....
........|.....
...|||||||||..
...|#~~~~~#|..
...|#~~~~~#|..
...|#~~~~~#|..
...|#######|.."""

    with open('test_input.txt', 'r') as test:
        test_ground = Ground(line.strip() for line in test)
        test_ground.run()
        assert expected == test_ground.show()


def test_count():
    with open('test_input.txt', 'r') as test:
        test_ground = Ground(line.strip() for line in test)
        test_ground.run()
        assert 57 == test_ground.count()


# Problematic case

def test_problem():
    expected = """\
..........+..........
.....................
.#.................#.
.#.................#.
.#.................#.
.#.................#.
.#.................#.
.#.................#.
.#......######.....#.
.#......#....#.....#.
.#......#....#.....#.
.#......######.....#.
.#.................#.
.#.................#.
.###################."""

    with open('problem_input.txt', 'r') as test:
        test_ground = Ground(line.strip() for line in test)
        test_ground.print()
        assert expected == test_ground.show()
        test_ground.run()
        test_ground.print()


if __name__ == '__main__':
    with open('../data/day17-input.txt', 'r') as file:
        ground = Ground(line.strip() for line in file)
        ground.run()
        print("Part1:", ground.count() - ground.real_min_y + 1)
        print("Part2:", ground.count_dry())
