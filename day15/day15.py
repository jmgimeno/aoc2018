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
        return "%s(x=%d, y=%d)" % (kind, self.x, self.y)


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


class Simulation:

    def __init__(self, lines):
        self.cave, self.units = parse_lines(lines)
        self.occupied_positions = {(u.x, u.y) for u in self.units}

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

    def round(self):
        sorted_units = sorted(self.units, key=lambda u: (u.y, u.x))
        for unit in sorted_units:
            if unit.is_alive:
                self.turn(unit)

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
            if c != '.' and self.units[c].kind != unit.kind:
                enemies.append(self.units[c])
        return min(enemies, key=lambda u: (u.hit_points, u.y , u.x)) \
                if len(enemies) > 0 else None

    def next_pos(self, unit):
        unit_pos = unit.x, unit.y
        targets = self.find_targets(unit)
        in_range = self.find_in_range(targets)
        reachable = self.find_reachable(unit_pos, in_range)
        nearest = self.find_nearest(unit_pos, reachable)
        chosen = self.find_chosen(nearest)
        return self.find_step(unit_pos, chosen)

    def find_targets(self, unit):
        return [target
                for target in self.units
                if target.kind != unit.kind and target.is_alive]

    def find_in_range(self, targets):
        return {pos
                for target in targets
                for pos in self.adjacent_to(target.x, target.y)}

    def find_reachable(self, begin, in_range):
        return {end for end in in_range if self.is_reachable(begin, end)}

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

    def distance(self, begin, end, visited=None):
        if visited is None:
            visited = set()
        if begin == end:
            return 0
        next_positions = {(x, y)
                          for (x, y) in self.adjacent_to(begin[0], begin[1])
                          if (x, y) not in self.occupied_positions | visited}
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
        x, y = self.next_pos(unit)
        self.cave[y][x] = self.cave[unit.y][unit.y]
        self.cave[unit.y][unit.x] = '.'
        unit.x, unit.y = x, y

    def attack(self, unit, enemy):
        enemy.hit_points -= unit.attack_power
        if enemy.hit_points <= 0:
            enemy.is_alive = False
            self.cave[enemy.y][enemy.x] = '.'


@pytest.fixture
def simulation():
    lines = ["#######",
             "#E..G.#",
             "#...#.#",
             "#.G.#G#",
             "#######"]
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
    expected = {(3, 1), (5, 1), (2, 2), (5, 2), (1, 3), (3, 3)}
    unit = Unit(x=1, y=1, kind=Unit.ELF)
    targets = simulation.find_targets(unit)
    assert simulation.find_in_range(targets) == expected


def test_find_reachable(simulation):
    expected = {(3, 1), (2, 2), (1, 3), (3, 3)}
    unit = Unit(x=1, y=1, kind=Unit.ELF)
    targets = simulation.find_targets(unit)
    in_range = simulation.find_in_range(targets)
    assert simulation.find_reachable((unit.x, unit.y), in_range) == expected


def test_find_reachable(simulation):
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
