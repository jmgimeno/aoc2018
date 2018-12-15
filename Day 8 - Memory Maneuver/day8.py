from collections import namedtuple

Node = namedtuple("Node", ["children", "metadata"])

def calc_part1(data):
    _, tree = read_tree(data, 0)
    return sum_metadata(tree)

def read_tree(data, idx):
    num_children = data[idx]
    num_metadata = data[idx+1]
    idx += 2
    children = []
    metadata = []
    for _ in range(num_children):
        idx, child = read_tree(data, idx)
        children.append(child)
    for _ in range(num_metadata):
        metadata.append(data[idx])
        idx += 1
    return idx, Node(children, metadata)

def sum_metadata(tree):
    return sum(tree.metadata) + sum(sum_metadata(child) for child in tree.children)

def parse(file):
    return [int(n) for n in file.read().split(" ")]

def part1(fname):
    with open(fname, "r") as file:
        return calc_part1(parse(file))

def test_part1():
    assert 36627 == part1("input.txt")

def calc_part2(data):
    _, tree = read_tree(data, 0)
    return value_at_root(tree)

def value_at_root(tree):
    if len(tree.children) == 0:
        return sum(tree.metadata)
    else:
        return sum( value_at_root(tree.children[idx-1]) 
                    for idx in tree.metadata
                    if idx > 0 and idx <= len(tree.children))

def part2(fname):
    with open(fname, "r") as file:
        return calc_part2(parse(file))

test_data = [int(c) for c in "2 3 0 3 10 11 12 1 1 0 1 99 2 1 1 2".split(" ")]

def test_calc_part1():
    assert 138 == calc_part1(test_data)

def test_calc_part2():
    assert 66 == calc_part2(test_data)

def test_part2():
    assert 16695 == part2("input.txt")

if __name__ == "__main__":
    print("Part1: ", part1("input.txt"))
    print("Part2: ", part2("input.txt"))
