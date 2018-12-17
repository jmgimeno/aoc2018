import collections
import re

Line = collections.namedtuple('Line', 'min_x max_x min_y max_y')

range_regexp = re.compile(r'\s*(?P<axis>[x|y])=(?P<min>\d+)(\.\.(?P<max>\d+))?\s*')


def parse_line(line):
    limits = [0] * 4
    for part in line.split(','):
        groups = range_regexp.match(part).groupdict()
        offset = 0 if groups['axis'] == 'x' else 2
        min_ = int(groups['min'])
        max_ = int(groups['max']) if groups['max'] else min_
        limits[offset] = min_
        limits[offset + 1] = max_
    return Line(*limits)


def parse_lines(lines):
    return [parse_line(line) for line in lines.split('\n')]


def test_parse_line():
    assert Line(495, 495, 2, 7) == parse_line('x=495, y=2..7')
    assert Line(495, 501, 7, 7) == parse_line('y=7, x=495..501')
    assert Line(501, 501, 3, 7) == parse_line('x=501, y=3..7')
    assert Line(498, 498, 2, 4) == parse_line('x=498, y=2..4')
    assert Line(506, 506, 1, 2) == parse_line('x=506, y=1..2')
    assert Line(498, 498, 10, 13) == parse_line('x=498, y=10..13')
    assert Line(504, 504, 10, 13) == parse_line('x=504, y=10..13')
    assert Line(498, 504, 13, 13) == parse_line('y=13, x=498..504')


def test_parse_lines():
    lines = """x=495, y=2..7
               y=7, x=495..501
               x=501, y=3..7
               x=498, y=2..4
               x=506, y=1..2
               x=498, y=10..13
               x=504, y=10..13
               y=13, x=498..504"""
    expected = [Line(495, 495, 2, 7), Line(495, 501, 7, 7), Line(501, 501, 3, 7),
                Line(498, 498, 2, 4), Line(506, 506, 1, 2), Line(498, 498, 10, 13),
                Line(504, 504, 10, 13), Line(498, 504, 13, 13)]

    assert expected == parse_lines(lines)
