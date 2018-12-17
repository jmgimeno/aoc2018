# All coordinates are positive

def grid_size(points):
    min_x = min(x for (x, _) in points)
    max_x = max(x for (x, _) in points)
    min_y = min(y for (_, y) in points)
    max_y = max(y for (_, y) in points)
    return min_x, max_x, min_y, max_y

def infinite_area(points):
    min_x, max_x, min_y, max_y = grid_size(points)
    result = set()
    for (x, y) in points:
        if x == min_x or x == max_x or y == min_y or y == max_y:
            result.add((x, y))
    return result

def manhattan(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return abs(x1 - x2) + abs(y1 - y2)


def calc_part1(points):
    min_x, max_x, min_y, max_y = grid_size(points)
    counters = {}
    for x in range(min_x, max_x+1):
        for y in range(min_y, max_y+1):
            min_d = float('inf')
            min_p = None
            for p in points:
                d = manhattan((x,y), p)
                if d < min_d:
                    min_d = d
                    min_p = p
                elif d == min_d:
                    min_p = None
            if min_p:
                counters[min_p] = counters.get(min_p, 0) + 1
                # Initially I didn't understand this condition (yes, I cheated)
                # The idea is that if the closest point to a point in the edge
                # is min_p, then min_p is an infinite area point !!!!
                # Yes, now I understand !!! :-D
                if x in (min_x, max_x) or y in (min_y, max_y):
                    counters[min_p] = float("-inf")
    return max(counters.values())

def calc_total_distances(points):
    min_x, max_x, min_y, max_y = grid_size(points)
    total_distances = {}
    for x in range(min_x, max_x+1):
        for y in range(min_y, max_y+1):
            total_distances.setdefault((x, y), 0)
            for p in points:
                total_distances[(x, y)] += manhattan((x,y), p)
    return total_distances

def parse(line):
    return tuple(map(int, line.split(",")))

def part1(fname):
    with open(fname, "r") as file:
        points = [parse(line) for line in file]
        return calc_part1(points)

test_points = [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)]

def test_infinite_area():
    assert {(1,1), (1, 6), (8, 3), (8, 9)} == infinite_area(test_points)

def test_calc_part1():
    assert 17 == calc_part1(test_points)

def calc_part2(points, limit):
    total_distances = calc_total_distances(points)
    return len([None for p in total_distances if total_distances[p] < limit])

def part2(fname):
    with open(fname, "r") as file:
        points = [parse(line) for line in file]
        return calc_part2(points, 10000)

# --------------------------------------------------------------
def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) -\
          (q[0] - p[0]) * (r[1] - q[1])
    return val # >0 - clockwise; 0 - colinear; <0 - counterclock

def leftmost_point(points):
    l = 0
    for i, _ in enumerate(points):
        if points[i][0] < points[l][0]:
            l = i
    return l

def convex_hull(points):
    n = len(points)
    hull = set()
    p = l = leftmost_point(points)
    while True:
        hull.add(points[p])
        q = (p + 1) % n
        for i in range(n):
            if orientation(points[p], points[i], points[q]) < 0:
                q = i
        p = q
        if q == l: break
    return hull

if __name__ == "__main__":
    print("Part1: ", part1("input.txt"))
    print("Part2: ", part2("input.txt"))
