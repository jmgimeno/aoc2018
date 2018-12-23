import collections
import operator
import re
import z3

line_regexp = re.compile(r'^pos=<(?P<x>-?\d+),(?P<y>-?\d+),(?P<z>-?\d+)>, r=(?P<r>\d+)$')

Nanobot = collections.namedtuple('Nanobot', 'x y z r')


def parse_line(line):
    match = line_regexp.match(line)
    return Nanobot(*map(int, match.groups()))


def distance(nano1, nano2):
    return sum(abs(nano1[xyz] - nano2[xyz]) for xyz in range(3))


def parse_file(fname):
    with open(fname, 'r') as file:
        return [parse_line(line.strip()) for line in file if len(line) > 0]


def part1(fname):
    nanobots = parse_file(fname)
    strongest = max(nanobots, key=operator.attrgetter('r'))
    return sum(1 for nano in nanobots if distance(nano, strongest) <= strongest.r)


def test_parse_line():
    assert parse_line('pos=<-13936329,35619897,41211497>, r=68603272') == \
           Nanobot(x=-13936329, y=35619897, z=41211497, r=68603272)


def test_part1():
    assert part1('test_input.txt') == 7


# The idea is not mine: use z3 to optimize an integer problem

def z3_abs(v):
    return z3.If(v >= 0, v, -v)


def part2(fname):
    nanobots = parse_file(fname)
    optimizer = z3.Optimize()
    # integer variables for the solution
    x, y, z = z3.Int('x'), z3.Int('y'), z3.Int('z')

    # maximum inside nanobots
    in_nanobots = []
    for idx, nanobot in enumerate(nanobots):
        in_nanobot = z3.Int('in_nanobot_%d' % (idx,))
        in_nanobots.append(in_nanobot)
        optimizer.add(in_nanobot == z3.If(z3_abs(x - nanobot.x)
                                          + z3_abs(y - nanobot.y)
                                          + z3_abs(z - nanobot.z) <= nanobot.r, 1, 0))
    total_in_nanobots = z3.Int('total_in_nanobots')
    optimizer.add(total_in_nanobots == sum(in_nanobots))
    optimizer.maximize(total_in_nanobots)

    # minimum x, y, x
    distance_to_origin = z3.Int('distance_to_origin')
    optimizer.add(distance_to_origin == z3_abs(x) + z3_abs(y) + z3_abs(z))
    optimizer.minimize(distance_to_origin)

    optimizer.check()
    return optimizer.model()[distance_to_origin]


def test_part2():
    assert part2('test_input2.txt') == 36


if __name__ == '__main__':
    print('Part1: ', part1('input.txt'))
    print('Part2: ', part2('input.txt'))
