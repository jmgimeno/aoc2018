import collections
import operator
import re

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


if __name__ == '__main__':
    print('Part1: ', part1('input.txt'))
