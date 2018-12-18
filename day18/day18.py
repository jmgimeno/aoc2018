import copy


class Simulation:

    def __init__(self, fname):
        self.map = load_initial(fname)
        self.height = len(self.map)
        self.width = len(self.map[0]) if self.height > 0 else 0

    def step(self):
        old_map = copy.deepcopy(self.map)
        for y, row in enumerate(old_map):
            for x, current in enumerate(row):
                open_ground, trees, lumbyard = self.count(old_map, x, y)
                self.map[y][x] = current
                if current == '.' and trees >= 3:
                    self.map[y][x] = '|'
                elif current == '|' and lumbyard >= 3:
                    self.map[y][x] = '#'
                elif current == '#' and (lumbyard == 0 or trees == 0):
                    self.map[y][x] = '.'

    def run(self, steps=1):
        viewed = set()
        for _ in range(steps):
            frozen_map = freeze(self.map)
            if frozen_map in viewed:
                print("Found !!!!!!")
                return
            else:
                viewed.add(frozen_map)
            self.step()

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

    def count(self, map_, x, y):
        neighborhood = self.neighborhood(x, y)
        open_ground = sum(1 for (xx, yy) in neighborhood if map_[yy][xx] == '.')
        trees = sum(1 for (xx, yy) in neighborhood if map_[yy][xx] == '|')
        lumberyard = sum(1 for (xx, yy) in neighborhood if map_[yy][xx] == '#')
        return open_ground, trees, lumberyard

    def show(self):
        return '\n'.join(''.join(c for c in row) for row in self.map)

def freeze(map_):
    return tuple(c for row in map_ for c in row)

def load_initial(fname):
    with open(fname, 'r') as file:
        return [[c for c in row.strip()] for row in file]

def part1(fname):
    simulation = Simulation(fname)
    simulation.run(10)
    trees = sum(1 for row in simulation.map for c in row if c == '|')
    lumber = sum(1 for row in simulation.map for c in row if c == '#')
    return trees * lumber

def part2(fname, steps):
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
    assert 1147 == part1('test_input.txt')

if __name__ == '__main__':
    print('Part1', part1('input.txt'))
    #print('Part1', part2('input.txt', 1000)) # 207640
    print('Part1', part2('input.txt', 1100)) # 207640