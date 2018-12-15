from collections import namedtuple
from pytest import fixture

Goblin = namedtuple('Goblin', 'x, y')
Elf = namedtuple('Elf', 'x, y')


def parse_lines(lines):
    units = set()
    cave = []
    for y, line in enumerate(lines):
        row = []
        for x, c in enumerate(line.strip()):
            if c == '#':
                row.append(False)
            elif c == '.':
                row.append(True)
            elif c == 'G':
                row.append(True)
                units.add(Goblin(x=x, y=y))
            elif c == 'E':
                row.append(True)
                units.add(Elf(x=x, y=y))
            else:
                raise Exception(
                    'impossible character %c at (%d, %d)' % (c, x, y))
        cave.append(row)
    return cave, units


class Simulation:

    def __init__(self, lines):
        self.cave, self.units = parse_lines(lines)
        self.occupied_positions = {(u.x, u.y) for u in self.units}

    def turn_order(self):
        return sorted(self.units, key=lambda unit: (unit.y, unit.x))

    def in_range(self, unit):
        possible_targets = {
            other for other in self.units if type(other) != type(unit)}
        return {(x, y)
                for target in possible_targets
                for (x, y) in adjacent_to(target) - self.occupied_positions
                if self.cave[y][x]}

    def can_reach(self, begin, end, visited=None):
        if visited is None:
            visited = set()
        if begin == end:
            return True
        next_positions = {(x, y)
                          for (x, y) in adjacent_to(begin) - self.occupied_positions - visited
                          if self.cave[y][x]}
        if len(next_positions) == 0:
            return False
        return any(self.can_reach(step, end, visited | {begin}) for step in next_positions)

    def reachable(self, unit):
        return {position for position in self.in_range(unit) if self.can_reach((unit.x, unit.y), position)}

    def distance(self, begin, end, visited=None):
        if visited is None:
            visited = set()
        if begin == end:
            return 0
        next_positions = {(x, y)
                          for (x, y) in adjacent_to(begin) - self.occupied_positions - visited
                          if self.cave[y][x]}
        if len(next_positions) == 0:
            return float("+inf")
        return 1 + min(self.distance(step, end, visited | {begin}) for step in next_positions)

    def nearest(self, begin):
        closests = set()
        min_distance = float("+inf")
        for end in self.in_range(begin):
            d = self.distance(begin, end)
            if d < min_distance:
                closests = {end}
                min_distance = d
            elif d == min_distance:
                closests.add(end)
        return closests
        


def adjacent_to(unit_or_tuple):
    if type(unit_or_tuple) == tuple:
        x, y = unit_or_tuple
    else:
        x, y = unit_or_tuple.x, unit_or_tuple.y
    return {(x, y-1), (x+1, y), (x, y+1), (x-1, y)}


@fixture
def simulation():
    lines = ["#######",
             "#E..G.#",
             "#...#.#",
             "#.G.#G#",
             "#######"]
    return Simulation(lines)


def test_parse_lines(simulation):
    expected_cave = [[False, False, False, False, False, False, False],
                     [False, True,  True,  True,  True,  True,  False],
                     [False, True,  True,  True,  False,  True,  False],
                     [False, True,  True,  True,  False,  True,  False],
                     [False, False, False, False, False, False, False]]
    expected_units = {Elf(x=1, y=1), Goblin(x=4, y=1),
                      Goblin(x=2, y=3), Goblin(x=5, y=3)}

    assert expected_cave == simulation.cave
    assert expected_units == simulation.units


def test_turn_order(simulation):
    assert [Elf(x=1, y=1), Goblin(x=4, y=1),
            Goblin(x=2, y=3), Goblin(x=5, y=3)] \
        == simulation.turn_order()


def test_in_range(simulation):
    assert {(3, 1), (5, 1), (2, 2), (5, 2), (1, 3), (3, 3)} \
        == simulation.in_range(Elf(x=1, y=1))


def test_can_reach(simulation):
    assert simulation.can_reach((1, 1), (1, 1))
    assert simulation.can_reach((1, 1), (3, 1))
    assert simulation.can_reach((1, 1), (2, 2))
    assert simulation.can_reach((1, 1), (1, 3))
    assert simulation.can_reach((1, 1), (3, 3))
    assert not simulation.can_reach((1, 1), (5, 1))
    assert not simulation.can_reach((1, 1), (5, 2))
    assert not simulation.can_reach((1, 1), (0, 0))


def test_reachable(simulation):
    assert {(3, 1), (2, 2), (1, 3), (3, 3)} \
        == simulation.reachable(Elf(x=1, y=1))

def test_min_distance(simulation):
    assert 0 == simulation.distance((1, 1), (1, 1))
    assert 2 == simulation.distance((1, 1), (3, 1))
    assert 2 == simulation.distance((1, 1), (2, 2))
    assert 2 == simulation.distance((1, 1), (1, 3))
    assert 4 == simulation.distance((1, 1), (3, 3))
    assert float("+inf") == simulation.distance((1, 1), (5, 1))
    assert float("+inf") == simulation.distance((1, 1), (5, 2))
    assert float("+inf") == simulation.distance((1, 1), (0, 0))

def _test_nearest(simulation):
    assert {(3, 1), (2, 2), (1, 3)} == simulation.nearest((1,1))