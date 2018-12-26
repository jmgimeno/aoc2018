import collections
import functools
import heapq
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

    def show(self):
        cave = []
        for row in self.cave:
            repr_row = []
            units_row = []
            for c in row:
                if c in ('#', '.'):
                    repr_row.append(c)
                else:
                    unit = self.units[c]
                    repr_row.append(kind_to_letter[unit.kind])
                    units_row.append('%s(%d)' % (kind_to_letter[unit.kind], unit.hit_points))
            cave.append('%s   %s' % (''.join(repr_row), ', '.join(units_row)))
        return '\n'.join(cave)

    @functools.lru_cache(maxsize=None)
    def adjacent_to(self, x, y):
        assert self.cave[y][x] != '#'
        return [(xx, yy)
                for (xx, yy) in [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]
                if self.cave[yy][xx] != '#']

    def run(self, max_rounds=float('inf')):
        finished = False
        self.finished_rounds = 0
        print('Initial cave')
        print(self.show())
        while not finished and self.finished_rounds < max_rounds:
            try:
                self.round()
                self.finished_rounds += 1
                print('\nFinished ', self.finished_rounds)
                print(self.show())
            except EndOfSimulation:
                finished = True
        return self.finished_rounds * self.sum_hit_points()

    def round(self):
        sorted_units = sorted((unit for unit in self.units if unit.is_alive),
                              key=lambda u: (u.y, u.x))
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
            if c != '.' and self.units[c].kind != unit.kind and self.units[c].is_alive:
                enemies.append(self.units[c])
        return min(enemies, key=lambda u: (u.hit_points, u.y, u.x)) \
            if len(enemies) > 0 else None

    def move_to_range(self, unit):
        targets = [(target.x, target.y)
                   for target in self.units
                   if target.kind != unit.kind
                   and target.is_alive]
        if len(targets) == 0:
            raise EndOfSimulation()
        chosen = self.chosen(unit, targets)
        print('Unit %s' % (unit,), end='')
        if chosen is None:
            print(' cannot get a target')
        else:
            x, y = self.next_pos(unit, chosen)
            print(' targets %s and moves to %s' % (chosen, (x, y)))
            self.cave[y][x] = self.cave[unit.y][unit.x]
            self.cave[unit.y][unit.x] = '.'
            unit.x, unit.y = x, y

    def chosen(self, unit, targets):
        in_range = {(x, y)
                    for (tx, ty) in targets
                    for (x, y) in self.adjacent_to(tx, ty)
                    if self.cave[y][x] == '.'}
        distances = collections.defaultdict(lambda: float('inf'))
        distances[(unit.x, unit.y)] = 0
        open_nodes = [(0, unit.y, unit.x)]
        while len(open_nodes) > 0:
            d, y, x = heapq.heappop(open_nodes)
            for (xx, yy) in self.adjacent_to(x, y):
                if self.cave[yy][xx] != '.':
                    continue
                if (xx, yy) in in_range:
                    return xx, yy
                new_d = 1 + d
                if new_d < distances[(xx, yy)]:
                    distances[(xx, yy)] = new_d
                    heapq.heappush(open_nodes, (distances[(xx, yy)], yy, xx))

    def next_pos(self, unit, chosen):
        cx, cy = chosen
        targets = {(x, y)
                   for (x, y) in self.adjacent_to(unit.x, unit.y)
                   if self.cave[y][x] == '.'}
        if chosen in targets:
            return chosen
        distances = collections.defaultdict(lambda: float('inf'))
        distances[(cx, cy)] = 0
        open_nodes = [(0, cy, cx)]
        while len(open_nodes) > 0:
            d, y, x = heapq.heappop(open_nodes)
            for (xx, yy) in self.adjacent_to(x, y):
                if self.cave[yy][xx] != '.':
                    continue
                if (xx, yy) in targets:
                    return xx, yy
                new_d = 1 + d
                if new_d < distances[(xx, yy)]:
                    distances[(xx, yy)] = new_d
                    heapq.heappush(open_nodes, (distances[(xx, yy)], yy, xx))

    def attack(self, unit, enemy):
        enemy.hit_points -= unit.attack_power
        if enemy.hit_points <= 0:
            enemy.is_alive = False
            self.cave[enemy.y][enemy.x] = '.'
        print('%s has attacked % s' %(unit, enemy))

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


def test_chosen(simulation):
    unit = Unit(x=1, y=1, kind=Unit.ELF)
    targets = [(target.x, target.y)
               for target in simulation.units
               if target.kind != unit.kind
               and target.is_alive]
    assert simulation.chosen(unit, targets) == (3, 1)


def test_next_pos(simulation):
    unit = Unit(x=1, y=1, kind=Unit.ELF)
    targets = [(target.x, target.y)
               for target in simulation.units
               if target.kind != unit.kind
               and target.is_alive]
    chosen = simulation.chosen(unit, targets)
    assert simulation.next_pos(unit, chosen) == (2, 1)


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


def test_run2(simulation2):
    expected = '''\
#######
#G....#
#.G...#
#.#.#G#
#...#.#
#....G#
#######'''

    assert simulation2.run() == 27730
    assert simulation2.finished_rounds == 47
    assert simulation2.sum_hit_points() == 590
    assert repr(simulation2) == expected
    assert simulation2.hit_points(1, 1) == 200
    assert simulation2.hit_points(2, 2) == 131
    assert simulation2.hit_points(5, 3) == 59
    assert simulation2.hit_points(5, 5) == 200


@pytest.fixture
def simulation3():
    lines = ['#######',
             '#G..#E#',
             '#E#E.E#',
             '#G.##.#',
             '#...#E#',
             '#...E.#',
             '#######']
    return Simulation(lines)


def test_run3(simulation3):
    expected = '''\
#######
#...#E#
#E#...#
#.E##.#
#E..#E#
#.....#
#######'''

    assert simulation3.run() == 36334
    assert simulation3.finished_rounds == 37
    assert simulation3.sum_hit_points() == 982
    assert repr(simulation3) == expected
    assert simulation3.hit_points(5, 1) == 200
    assert simulation3.hit_points(1, 2) == 197
    assert simulation3.hit_points(2, 3) == 185
    assert simulation3.hit_points(1, 4) == 200
    assert simulation3.hit_points(5, 4) == 200


@pytest.fixture
def simulation4():
    lines = ['#######',
             '#E..EG#',
             '#.#G.E#',
             '#E.##E#',
             '#G..#.#',
             '#..E#.#',
             '#######']
    return Simulation(lines)


def test_run4(simulation4):
    expected = '''\
#######
#.E.E.#
#.#E..#
#E.##.#
#.E.#.#
#...#.#
#######'''

    assert simulation4.run() == 39514
    assert simulation4.finished_rounds == 46
    assert simulation4.sum_hit_points() == 859
    assert repr(simulation4) == expected
    assert simulation4.hit_points(2, 1) == 164
    assert simulation4.hit_points(4, 1) == 197
    assert simulation4.hit_points(3, 2) == 200
    assert simulation4.hit_points(1, 3) == 98
    assert simulation4.hit_points(2, 4) == 200


@pytest.fixture
def simulation5():
    lines = ['#######',
             '#E.G#.#',
             '#.#G..#',
             '#G.#.G#',
             '#G..#.#',
             '#...E.#',
             '#######']
    return Simulation(lines)


def test_run5(simulation5):
    expected = '''\
#######
#G.G#.#
#.#G..#
#..#..#
#...#G#
#...G.#
#######'''

    assert simulation5.run() == 27755
    assert simulation5.finished_rounds == 35
    assert simulation5.sum_hit_points() == 793
    assert repr(simulation5) == expected
    assert simulation5.hit_points(1, 1) == 200
    assert simulation5.hit_points(3, 1) == 98
    assert simulation5.hit_points(3, 2) == 200
    assert simulation5.hit_points(5, 4) == 95
    assert simulation5.hit_points(4, 5) == 200


@pytest.fixture
def simulation6():
    lines = ['#######',
             '#.E...#',
             '#.#..G#',
             '#.###.#',
             '#E#G#G#',
             '#...#G#',
             '#######']
    return Simulation(lines)


def test_run6(simulation6):
    expected = '''\
#######
#.....#
#.#G..#
#.###.#
#.#.#.#
#G.G#G#
#######'''

    assert simulation6.run() == 28944
    assert simulation6.finished_rounds == 54
    assert simulation6.sum_hit_points() == 536
    assert repr(simulation6) == expected
    assert simulation6.hit_points(3, 2) == 200
    assert simulation6.hit_points(1, 5) == 98
    assert simulation6.hit_points(3, 5) == 38
    assert simulation6.hit_points(5, 5) == 200


@pytest.fixture
def simulation7():
    lines = ['#########',
             '#G......#',
             '#.E.#...#',
             '#..##..G#',
             '#...##..#',
             '#...#...#',
             '#.G...G.#',
             '#.....G.#',
             '#########']
    return Simulation(lines)


def test_run7(simulation7):
    expected = '''\
#########
#.G.....#
#G.G#...#
#.G##...#
#...##..#
#.G.#...#
#.......#
#.......#
#########'''

    assert simulation7.run() == 18740
    assert simulation7.finished_rounds == 20
    assert simulation7.sum_hit_points() == 937
    assert repr(simulation7) == expected
    assert simulation7.hit_points(2, 1) == 137
    assert simulation7.hit_points(1, 2) == 200
    assert simulation7.hit_points(3, 2) == 200
    assert simulation7.hit_points(2, 3) == 200
    assert simulation7.hit_points(2, 5) == 200


def part1(fname):
    with open(fname, 'r') as file:
        lines = [line.strip() for line in file]
        simulation = Simulation(lines)
        result = simulation.run()
        print("Finished rounds", simulation.finished_rounds)
        print("Sum of points", simulation.sum_hit_points())
        return result

if __name__ == '__main__':

    print("Part1: ", part1('input.txt'))
