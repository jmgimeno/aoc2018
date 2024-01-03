import functools


class Simulation:

    def __init__(self, fname):
        self.map = load_initial(fname)
        self.height = len(self.map)
        self.width = len(self.map[0]) if self.height > 0 else 0
        self.old_map = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def step(self):
        self.old_map, self.map = self.map, self.old_map  # double buffering
        for y, row in enumerate(self.old_map):
            for x, current in enumerate(row):
                neighborhood = self.neighborhood(x, y)
                trees = sum(1 for (xx, yy) in neighborhood if self.old_map[yy][xx] == '|')
                lumberyard = sum(1 for (xx, yy) in neighborhood if self.old_map[yy][xx] == '#')
                self.map[y][x] = current
                if current == '.' and trees >= 3:
                    self.map[y][x] = '|'
                elif current == '|' and lumberyard >= 3:
                    self.map[y][x] = '#'
                elif current == '#' and (lumberyard == 0 or trees == 0):
                    self.map[y][x] = '.'

    def run(self, steps=1):
        last_seen = {}
        step = 0
        while step < steps:
            hashable = self.show()
            if hashable in last_seen:
                remaining = (steps - step) % (step - last_seen[hashable])
                step = steps - remaining
                last_seen = {}
            else:
                last_seen[hashable] = step
            self.step()
            step += 1

    @functools.lru_cache(maxsize=None)
    def neighborhood(self, x, y):
        neighbors = []
        for dx in [-1, 0, +1]:
            xx = x + dx
            if 0 > xx or xx >= self.width:
                continue
            for dy in [-1, 0, +1]:
                yy = y + dy
                if 0 > yy or yy >= self.height or (xx == x and yy == y):
                    continue
                neighbors.append((xx, yy))
        return neighbors

    def show(self):
        return '\n'.join(''.join(c for c in row) for row in self.map)


def load_initial(fname):
    with open(fname, 'r') as file:
        return [[c for c in row.strip()] for row in file]


def part(fname, steps):
    simulation = Simulation(fname)
    simulation.run(steps)
    trees = sum(1 for row in simulation.map for c in row if c == '|')
    lumber = sum(1 for row in simulation.map for c in row if c == '#')
    return trees * lumber


def test_load_initial():
    expected = list(map(list, ['.#.#...|#.',
                               '.....#|##|',
                               '.|..|...#.',
                               '..|#.....#',
                               '#.#|||#|#|',
                               '...#.||...',
                               '.|....|...',
                               '||...#|.#|',
                               '|.||||..|.',
                               '...#.|..|.']))

    assert expected == load_initial('test_input.txt')


def test_one_step():
    expected = """\
.......##.
......|###
.|..|...#.
..|#||...#
..##||.|#|
...#||||..
||...|||..
|||||.||.|
||||||||||
....||..|."""

    simulation = Simulation('test_input.txt')
    simulation.step()
    assert expected == simulation.show()


def test_ten_steps():
    expected = """\
.||##.....
||###.....
||##......
|##.....##
|##.....##
|##....##|
||##.####|
||#####|||
||||#|||||
||||||||||"""

    simulation = Simulation('test_input.txt')
    simulation.run(10)
    assert expected == simulation.show()


def test_part1():
    assert 1147 == part('test_input.txt', 10)


if __name__ == '__main__':
    print('Part1', part('../data/day18-input.txt', 10))
    print('Part2', part('../data/day18-input.txt', 1000000000))
