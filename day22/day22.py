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
State = collections.namedtuple('State', 'distance region equipment')


class Cave:
    def __init__(self, depth, target):
        self.depth = depth
        self.target = target

    def type_(self, region):
        return type_(region, self.depth, self.target)

    def explore(self):
        visited = set()
        states = []
        heapq.heappush(states, State(distance=0, region=(0, 0), equipment=TORCH))
        while True:
            state = heapq.heappop(states)
            if state in visited:
                continue
            else:
                visited.add(state)
            if state.region == self.target and state.equipment == TORCH:
                return state.distance
            for adjacent in neighborhood(state.region):
                if state.equipment in COMPATIBILITY[self.type_(adjacent)]:
                    heapq.heappush(states,
                                   State(distance=1 + state.distance, region=adjacent, equipment=state.equipment))
            for other_equipment in [CLIMBING_GEAR, TORCH, NEITHER]:
                if other_equipment != state.equipment:
                    heapq.heappush(states,
                                   State(distance=7 + state.distance, region=state.region, equipment=other_equipment))


def neighborhood(region):
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


if __name__ == '__main__':
    print("Part1: ", risk_level(8112, (13, 743)))
    print("Part2: ", explore(8112, (13, 743)))
