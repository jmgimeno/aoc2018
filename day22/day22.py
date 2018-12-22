import collections
import functools
import heapq

ROCKY, WET, NARROW = range(3)


@functools.lru_cache(maxsize=None)
def geologic_index(region, depth, target):
    x, y = region
    if region == (0, 0) or region == target:
        return 0
    elif y == 0:
        return x * 16807
    elif x == 0:
        return y * 48271
    else:
        return erosion_level((x - 1, y), depth, target) * erosion_level((x, y - 1), depth, target)


@functools.lru_cache(maxsize=None)
def erosion_level(region, depth, target):
    return (geologic_index(region, depth, target) + depth) % 20183


def type_(region, depth, target):
    return erosion_level(region, depth, target) % 3


def risk_level(depth, target):
    width, height = target
    return sum(type_((x, y), depth, target) for x in range(width + 1) for y in range(height + 1))


def test_geologic_index():
    assert geologic_index((0, 0), 510, (10, 10)) == 0
    assert geologic_index((1, 0), 510, (10, 10)) == 16807
    assert geologic_index((0, 1), 510, (10, 10)) == 48271
    assert geologic_index((1, 1), 510, (10, 10)) == 145722555
    assert geologic_index((10, 10), 510, (10, 10)) == 0


def test_erosion_level():
    assert erosion_level((0, 0), 510, (10, 10)) == 510
    assert erosion_level((1, 0), 510, (10, 10)) == 17317
    assert erosion_level((0, 1), 510, (10, 10)) == 8415
    assert erosion_level((1, 1), 510, (10, 10)) == 1805
    assert erosion_level((10, 10), 510, (10, 10)) == 510


def test_type():
    assert type_((0, 0), 510, (10, 10)) == ROCKY
    assert type_((1, 0), 510, (10, 10)) == WET
    assert type_((0, 1), 510, (10, 10)) == ROCKY
    assert type_((1, 1), 510, (10, 10)) == NARROW
    assert type_((10, 10), 510, (10, 10)) == ROCKY


def test_risk_level():
    assert risk_level(510, (10, 10)) == 114


# Part 2

CLIMBING_GEAR, TORCH, NEITHER = range(3)
COMPATIBILITY = {ROCKY: {CLIMBING_GEAR, TORCH}, WET: {CLIMBING_GEAR, NEITHER}, NARROW: {TORCH, NEITHER}}

Node = collections.namedtuple('Node', 'fscore state')
State = collections.namedtuple('State', 'region equipment')


class Cave:
    def __init__(self, depth, target):
        self.depth = depth
        self.target = target

    def type_(self, region):
        return type_(region, self.depth, self.target)

    def explore(self):
        fscore = collections.defaultdict(lambda: float('inf'))
        gscore = {}
        start = State(region=(0, 0), equipment=TORCH)

        gscore[start] = 0
        fscore[start] = self.heuristic(start)

        open_states = {start}
        closed_states = set()

        while True:
            current_state = min(open_states, key=lambda s: fscore[s])
            open_states.remove(current_state)

            if current_state.region == self.target and current_state.equipment == TORCH:
                return gscore[current_state]

            closed_states.add(current_state)

            for next_state, distance in self.neighborhood(current_state):

                if next_state in closed_states:
                    continue

                tentative_gscore = gscore[current_state] + distance

                if next_state not in open_states:
                    open_states.add(next_state)
                elif tentative_gscore > gscore[next_state]:
                    continue

                gscore[next_state] = tentative_gscore
                fscore[next_state] = tentative_gscore + self.heuristic(next_state)

    def heuristic(self, state):
        region = state.region
        return abs(self.target[0] - region[0]) + abs(self.target[1] - region[1])

    def neighborhood(self, current):
        next_states_and_distances = []
        for next_region in adjacent(current.region):
            if current.equipment in COMPATIBILITY[self.type_(next_region)]:
                next_states_and_distances.append((State(region=next_region, equipment=current.equipment), 1))
        for equipment in [CLIMBING_GEAR, TORCH, NEITHER]:
            if equipment != current.equipment and equipment in COMPATIBILITY[self.type_(current.region)]:
                next_states_and_distances.append((State(region=current.region, equipment=equipment), 7))
        return next_states_and_distances


def adjacent(region):
    x, y = region
    moves = []
    if x > 0:
        moves.append((x - 1, y))
    if y > 0:
        moves.append((x, y - 1))
    return moves + [(x + 1, y), (x, y + 1)]


def explore(depth, target):
    return Cave(depth, target).explore()


def test_cave():
    cave = Cave(510, (10, 10))
    assert cave.type_((0, 0)) == ROCKY
    assert cave.type_((1, 0)) == WET
    assert cave.type_((0, 1)) == ROCKY
    assert cave.type_((1, 1)) == NARROW
    assert cave.type_((10, 10)) == ROCKY


def test_explore():
    cave = Cave(510, (10, 10))
    assert cave.explore() == 45

def _test_part2():
    cave = Cave(8112, (13, 743))
    assert cave.explore() == 1010

if __name__ == '__main__':
    print("Part1: ", risk_level(8112, (13, 743)))
    print("Part2: ", explore(8112, (13, 743)))
