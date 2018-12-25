import numpy as np
import scipy.cluster.hierarchy as hc


def parse_file(fname):
    with open(fname, 'r') as file:
        return np.array([[int(elem)
                          for elem in line.strip().split(',')]
                         for line in file])


def part1(fname, max_dist):
    data = parse_file(fname)
    linkage_matrix = hc.linkage(data, method='single', metric='cityblock')
    clustering = hc.fcluster(linkage_matrix, max_dist, criterion='distance')
    return clustering.max()


def test_part1():
    assert part1('test_input1.txt', 3) == 2
    assert part1('test_input2.txt', 3) == 4
    assert part1('test_input3.txt', 3) == 3
    assert part1('test_input4.txt', 3) == 8


if __name__ == '__main__':
    print("Part1: ", part1('input.txt', 3))
