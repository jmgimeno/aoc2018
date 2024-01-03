from re import compile

def parse(line):
    regexp = compile(r"^#(?P<id>\d+) @ (?P<x>\d+),(?P<y>\d+): (?P<w>\d+)x(?P<h>\d+)$")
    return tuple(int(g) for g in regexp.match(line).groups())

def test_parse():
    assert (1, 286, 440, 19, 24) == parse("#1 @ 286,440: 19x24")

def over(dim1, dim2):
    x1, w1 = dim1
    x2, w2 = dim2
    if (x1 > x2):
        return over((x2,w2), (x1,w1))
    if x2 < x1 + w1:
        return x2, min(x1+w1-x2, w2)
    return (0, 0)

def test_over():
    assert (3,2) == over((1,4), (3,4))
    assert (0,0) == over((1,4), (5,2))

def overlaps(claim1, claim2):
    _, x1, y1, w1, h1 = claim1
    _, x2, y2, w2, h2 = claim2
    _, w = over((x1,w1), (x2,w2))
    _, h = over((y1,h1), (y2,h2))
    return w != 0 and h != 0

def test_overlap():
    assert overlaps((1,1,3,4,4), (1,3,1,4,4))
    assert overlaps((1,3,1,4,4), (1,1,3,4,4))
    assert not overlaps((1,1,3,4,4), (3,5,5,2,2))
    assert not overlaps((3,5,5,2,2), (1,1,3,4,4))

def total_overlap(claims):
    counter = {}
    for _, x, y, w, h in claims:
        for xx in range(x,x+w):
            row = counter.setdefault(xx, {})
            for yy in range(y,y+h):
                hits = row.setdefault(yy, 0)
                row[yy] = hits + 1
    more_than_one = 0
    for row in counter.values():
        for c in row.values(): 
            if c > 1: more_than_one += 1
    return more_than_one

def test_total_overlap():
    claims = [(1,1,3,4,4), (2,3,1,4,4), (3,5,5,2,2)]
    assert 4 == total_overlap(claims)

def part1(fname):
    with open(fname, "r") as file:
        return total_overlap(parse(line) for line in file)

def not_overlaps(claims):
    for claim1 in claims:
        found = False
        for claim2 in claims:
            if claim1 == claim2: continue
            if overlaps(claim1, claim2):
                found = True
                break
        if not found:
            return claim1[0]

def test_not_overlaps():
    claims = [(1,1,3,4,4), (2,3,1,4,4), (3,5,5,2,2)]
    assert 3 == not_overlaps(claims)

def part2(fname):
    with open(fname, "r") as file:
        return not_overlaps([parse(line) for line in file])

if __name__ == "__main__":
    print("Part1: ", part1("../data/day3-input.txt"))
    print("Part2: ", part2("../data/day3-input.txt"))