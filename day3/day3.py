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

def overlap(claim1, claim2):
    _, x1, y1, w1, h1 = claim1
    _, x2, y2, w2, h2 = claim2
    (x, w) = over((x1, w1),(x2, w2))
    if w == 0:
        return (0,0,0,0)
    (y, h) = over((y1,h1), (y2,h2))
    if h == 0:
        return (0,0,0,0)
    return (x,y,w,h)

def test_overlap():
    assert (3,3,2,2) == overlap((1,1,3,4,4),(1,3,1,4,4))
    assert (0,0,0,0) == overlap((1,1,3,4,4),(3,5,5,2,2))

def total_overlap(claims):
    pass

def test_total_overlap():
    claims = [(1,1,3,4,4), (2,3,1,4,4), (3,5,5,2,2)]
    assert 4 == total_overlap(claims)

def part1(fname):
    with open(fname, "r") as file:
        return total_overlap(parse(line) for line in file)

if __name__ == "__main__":
    print("Part1: ", part1("input.txt"))