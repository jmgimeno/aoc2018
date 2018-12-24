import functools

import pytest


class Unit:
    ELF, GOBLIN = range(2)

    def __init__(self, x, y, kind, hit_points=200, attack_power=3):
        self.x = x
        self.y = y
        self.kind = kind
        self.hit_points = hit_points
        self.attack_power = attack_power
        self.is_alive = True

    def __eq__(self, other):
        return (self.x == other.x
                and self.y == other.y
                and self.kind == other.kind)

    def __repr__(self):
        kind = ['Elf', 'Goblin'][self.kind]
        return "%s(x=%d, y=%d, hp=%d)" % (kind, self.x, self.y, self.hit_points)


letter_to_kind = {'G': Unit.GOBLIN, 'E': Unit.ELF}
kind_to_letter = {Unit.GOBLIN: 'G', Unit.ELF: 'E'}


def parse_lines(lines):
    cave = []
    units = []
    for y, line in enumerate(lines):
        row = []
        for x, c in enumerate(line.strip()):
            if c in ('#', '.'):
                row.append(c)
            elif c in ('G', 'E'):
                units.append(Unit(x=x, y=y, kind=letter_to_kind[c]))
                row.append(len(units) - 1)
            else:
                raise Exception(
                    'impossible character %c at (%d, %d)' % (c, x, y))
        cave.append(row)
    return cave, units


class EndOfSimulation(Exception):
    pass


class Simulation:

    def __init__(self, lines):
        self.cave, self.units = parse_lines(lines)
        self.occupied_positions = {(u.x, u.y) for u in self.units if u.is_alive}
        self.finished_rounds = 0

    def __repr__(self):
        repr_cave = []
        for row in self.cave:
            repr_row = []
            for c in row:
                if c in ('#', '.'):
                    repr_row.append(c)
                else:
                    repr_row.append(kind_to_letter[self.units[c].kind])
            repr_cave.append(''.join(repr_row))
        return '\n'.join(repr_cave)

    @functools.lru_cache(maxsize=None)
    def adjacent_to(self, x, y):
        assert self.cave[y][x] != '#'
        return [(xx, yy)
                for (xx, yy) in [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]
                if self.cave[yy][xx] != '#']

    def run(self, max_rounds=float('inf')):
        finished = False
        self.finished_rounds = 0
        while not finished and self.finished_rounds < max_rounds:
            try:
                self.round()
                self.finished_rounds += 1
                print("Finished ", self.finished_rounds)
            except EndOfSimulation:
                finished = True
        return self.finished_rounds * self.sum_hit_points()

    def round(self):
        sorted_units = sorted((unit for unit in self.units if unit.is_alive),
                              key=lambda u: (u.y, u.x))
        for unit in sorted_units:
            if unit.is_alive:
                self.turn(unit)
                self.occupied_positions = {(u.x, u.y) for u in self.units if u.is_alive}

    def turn(self, unit):
        if not self.enemy_in_range(unit):
            self.move_to_range(unit)
        enemy = self.enemy_in_range(unit)
        if enemy:
            self.attack(unit, enemy)

    def enemy_in_range(self, unit):
        enemies = []
        for (x, y) in self.adjacent_to(unit.x, unit.y):
            c = self.cave[y][x]
            if c != '.' and self.units[c].kind != unit.kind and self.units[c].is_alive:
                enemies.append(self.units[c])
        return min(enemies, key=lambda u: (u.hit_points, u.y, u.x)) \
            if len(enemies) > 0 else None

    def next_pos(self, unit):
        unit_pos = unit.x, unit.y
        targets = self.find_targets(unit)
        if len(targets) == 0:
            raise EndOfSimulation()
        in_range = self.find_in_range(targets)
        if len(in_range) == 0:
            return
        reachable = self.find_reachable(unit_pos, in_range)
        if len(reachable) == 0:
            return
        nearest = self.find_nearest(unit_pos, reachable)
        if len(nearest) == 0:
            return
        chosen = self.find_chosen(nearest)
        return self.find_step(unit_pos, chosen)

    def find_targets(self, unit):
        return [target
                for target in self.units
                if target.kind != unit.kind and target.is_alive]

    def find_in_range(self, targets):
        return [pos
                for target in targets
                for pos in self.adjacent_to(target.x, target.y)]

    def find_reachable(self, begin, in_range):
        return [end for end in in_range if self.is_reachable(begin, end)]

    def is_reachable(self, begin, end, visited=None):
        if not visited:
            visited = set()
        if begin == end:
            return True
        next_positions = ((x, y)
                          for (x, y) in self.adjacent_to(begin[0], begin[1])
                          if (x, y) not in self.occupied_positions | visited)
        return any(self.is_reachable(step, end, visited | {begin})
                   for step in next_positions)

    @functools.lru_cache(maxsize=None)
    def calc_distance(self, begin, end):
        return self.distance(begin, end)

    def distance(self, begin, end, visited=None):
        if visited is None:
            visited = set()
        if begin == end:
            return 0
        next_positions = [(x, y)
                          for (x, y) in self.adjacent_to(begin[0], begin[1])
                          if (x, y) not in self.occupied_positions | visited]
        if len(next_positions) == 0:
            return float("+inf")
        return 1 + min(self.distance(step, end, visited | {begin})
                       for step in next_positions)

    def find_nearest(self, begin, reachable):
        nearest = set()
        min_distance = float("+inf")
        for end in reachable:
            d = self.distance(begin, end)
            if d < min_distance:
                nearest = {end}
                min_distance = d
            elif d == min_distance:
                nearest.add(end)
        return nearest

    def find_chosen(self, nearest):
        return min(nearest, key=lambda p: (p[1], p[0]))

    def find_step(self, begin, chosen):
        return min((neighbour for neighbour in self.adjacent_to(begin[0], begin[1])),
                   key=lambda xy: (self.distance(xy, chosen), xy[1], xy[0]))

    def move_to_range(self, unit):
        next_pos = self.next_pos(unit)
        if next_pos is not None:
            x, y = next_pos
            self.cave[y][x] = self.cave[unit.y][unit.x]
            self.cave[unit.y][unit.x] = '.'
            unit.x, unit.y = x, y
            self.calc_distance.cache_clear()

    def attack(self, unit, enemy):
        enemy.hit_points -= unit.attack_power
        if enemy.hit_points <= 0:
            enemy.is_alive = False
            self.cave[enemy.y][enemy.x] = '.'

    def hit_points(self, x, y):
        for unit in self.units:
            if unit.x == x and unit.y == y and unit.is_alive:
                return unit.hit_points

    def sum_hit_points(self):
        return sum(unit.hit_points for unit in self.units if unit.is_alive)


@pytest.fixture
def simulation():
    lines = ['#######',
             '#E..G.#',
             '#...#.#',
             '#.G.#G#',
             '#######']
    return Simulation(lines)


def test_parse_lines(simulation):
    expected_cave = [['#', '#', '#', '#', '#', '#', '#'],
                     ['#', 0, '.', '.', 1, '.', '#'],
                     ['#', '.', '.', '.', '#', '.', '#'],
                     ['#', '.', 2, '.', '#', 3, '#'],
                     ['#', '#', '#', '#', '#', '#', '#']]
    expected_units = [Unit(x=1, y=1, kind=Unit.ELF),
                      Unit(x=4, y=1, kind=Unit.GOBLIN),
                      Unit(x=2, y=3, kind=Unit.GOBLIN),
                      Unit(x=5, y=3, kind=Unit.GOBLIN)]
    assert expected_cave == simulation.cave
    assert expected_units == simulation.units


def test_repr(simulation):
    expected = '''\
#######
#E..G.#
#...#.#
#.G.#G#
#######'''
    assert repr(simulation) == expected


def test_find_targets(simulation):
    expected = [Unit(x=4, y=1, kind=Unit.GOBLIN),
                Unit(x=2, y=3, kind=Unit.GOBLIN),
                Unit(x=5, y=3, kind=Unit.GOBLIN)]
    assert simulation.find_targets(Unit(x=1, y=1, kind=Unit.ELF)) == expected


def test_find_in_range(simulation):
    expected = [(3, 1), (5, 1), (2, 2), (5, 2), (1, 3), (3, 3)]
    unit = Unit(x=1, y=1, kind=Unit.ELF)
    targets = simulation.find_targets(unit)
    assert set(simulation.find_in_range(targets)) == set(expected)


def test_find_reachable(simulation):
    expected = [(3, 1), (2, 2), (1, 3), (3, 3)]
    unit = Unit(x=1, y=1, kind=Unit.ELF)
    targets = simulation.find_targets(unit)
    in_range = simulation.find_in_range(targets)
    assert set(simulation.find_reachable((unit.x, unit.y), in_range)) == set(expected)


def test_find_nearest(simulation):
    expected = {(3, 1), (2, 2), (1, 3)}
    unit = Unit(x=1, y=1, kind=Unit.ELF)
    targets = simulation.find_targets(unit)
    in_range = simulation.find_in_range(targets)
    reachable = simulation.find_reachable((unit.x, unit.y), in_range)
    assert simulation.find_nearest((unit.x, unit.y), reachable) == expected


def test_find_chosen(simulation):
    unit = Unit(x=1, y=1, kind=Unit.ELF)
    targets = simulation.find_targets(unit)
    in_range = simulation.find_in_range(targets)
    reachable = simulation.find_reachable((unit.x, unit.y), in_range)
    nearest = simulation.find_nearest((unit.x, unit.y), reachable)
    assert simulation.find_chosen(nearest) == (3, 1)


def test_find_step(simulation):
    unit = Unit(x=1, y=1, kind=Unit.ELF)
    targets = simulation.find_targets(unit)
    in_range = simulation.find_in_range(targets)
    reachable = simulation.find_reachable((unit.x, unit.y), in_range)
    nearest = simulation.find_nearest((unit.x, unit.y), reachable)
    chosen = simulation.find_chosen(nearest)
    assert simulation.find_step((unit.x, unit.y), chosen) == (2, 1)


def test_next_pos(simulation):
    unit = Unit(x=1, y=1, kind=Unit.ELF)
    assert simulation.next_pos(unit) == (2, 1)


@pytest.fixture
def simulation2():
    lines = ['#######',
             '#.G...#',
             '#...EG#',
             '#.#.#G#',
             '#..G#E#',
             '#.....#',
             '#######']
    return Simulation(lines)


def test_simulation2(simulation2):
    expected = '''\
#######
#.G...#
#...EG#
#.#.#G#
#..G#E#
#.....#
#######'''
    assert repr(simulation2) == expected


def test_round1(simulation2):
    expected = '''\
#######
#..G..#
#...EG#
#.#G#G#
#...#E#
#.....#
#######'''

    simulation2.run(1)
    assert repr(simulation2) == expected
    assert simulation2.hit_points(3, 1) == 200
    assert simulation2.hit_points(4, 2) == 197
    assert simulation2.hit_points(5, 2) == 197
    assert simulation2.hit_points(3, 3) == 200
    assert simulation2.hit_points(5, 3) == 197
    assert simulation2.hit_points(5, 4) == 197


def test_round2(simulation2):
    expected = '''\
#######
#...G.#
#..GEG#
#.#.#G#
#...#E#
#.....#
#######'''

    simulation2.run(2)
    assert repr(simulation2) == expected
    assert simulation2.hit_points(4, 1) == 200
    assert simulation2.hit_points(3, 2) == 200
    assert simulation2.hit_points(4, 2) == 188
    assert simulation2.hit_points(5, 3) == 194
    assert simulation2.hit_points(5, 3) == 194
    assert simulation2.hit_points(5, 4) == 194


def test_round23(simulation2):
    expected = '''\
#######
#...G.#
#..G.G#
#.#.#G#
#...#E#
#.....#
#######'''

    simulation2.run(23)
    assert repr(simulation2) == expected
    assert simulation2.hit_points(4, 1) == 200
    assert simulation2.hit_points(3, 2) == 200
    assert simulation2.hit_points(5, 2) == 131
    assert simulation2.hit_points(5, 3) == 131
    assert simulation2.hit_points(5, 4) == 131


def test_round24(simulation2):
    expected = '''\
#######
#..G..#
#...G.#
#.#G#G#
#...#E#
#.....#
#######'''

    simulation2.run(24)
    assert repr(simulation2) == expected
    assert simulation2.hit_points(3, 1) == 200
    assert simulation2.hit_points(4, 2) == 131
    assert simulation2.hit_points(3, 3) == 200
    assert simulation2.hit_points(5, 3) == 128
    assert simulation2.hit_points(5, 4) == 128


def test_round25(simulation2):
    expected = '''\
#######
#.G...#
#..G..#
#.#.#G#
#..G#E#
#.....#
#######'''

    simulation2.run(25)
    assert repr(simulation2) == expected
    assert simulation2.hit_points(2, 1) == 200
    assert simulation2.hit_points(3, 2) == 131
    assert simulation2.hit_points(5, 3) == 125
    assert simulation2.hit_points(3, 4) == 200
    assert simulation2.hit_points(5, 4) == 125


def test_round26(simulation2):
    expected = '''\
#######
#G....#
#.G...#
#.#.#G#
#...#E#
#..G..#
#######'''

    simulation2.run(26)
    assert repr(simulation2) == expected
    assert simulation2.hit_points(1, 1) == 200
    assert simulation2.hit_points(2, 2) == 131
    assert simulation2.hit_points(5, 3) == 122
    assert simulation2.hit_points(5, 4) == 122
    assert simulation2.hit_points(3, 5) == 200


def test_round27(simulation2):
    expected = '''\
#######
#G....#
#.G...#
#.#.#G#
#...#E#
#...G.#
#######'''

    simulation2.run(27)
    assert repr(simulation2) == expected
    assert simulation2.hit_points(1, 1) == 200
    assert simulation2.hit_points(2, 2) == 131
    assert simulation2.hit_points(5, 3) == 119
    assert simulation2.hit_points(5, 4) == 119
    assert simulation2.hit_points(4, 5) == 200


def test_round28(simulation2):
    expected = '''\
#######
#G....#
#.G...#
#.#.#G#
#...#E#
#....G#
#######'''

    simulation2.run(28)
    assert repr(simulation2) == expected
    assert simulation2.hit_points(1, 1) == 200
    assert simulation2.hit_points(2, 2) == 131
    assert simulation2.hit_points(5, 3) == 116
    assert simulation2.hit_points(5, 4) == 113
    assert simulation2.hit_points(5, 5) == 200


def test_round47(simulation2):
    expected = '''\
#######
#G....#
#.G...#
#.#.#G#
#...#.#
#....G#
#######'''

    simulation2.run(47)
    assert repr(simulation2) == expected
    assert simulation2.hit_points(1, 1) == 200
    assert simulation2.hit_points(2, 2) == 131
    assert simulation2.hit_points(5, 3) == 59
    assert simulation2.hit_points(5, 5) == 200


def test_run(simulation2):
    assert simulation2.run() == 27730


def part1(fname):
    with open(fname, 'r') as file:
        lines = [line.strip() for line in file]
        simulation = Simulation(lines)
        return simulation.run()


if __name__ == '__main__':
    print("Part1: ", part1('input.txt'))
