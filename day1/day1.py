from itertools import cycle

def part1(fname):
    with open(fname, "r") as file:
        return part1_elems(file.readlines())

def part1_elems(elems):
    return sum(int(elem) for elem in elems)

def part2(fname):
    with open(fname, "r") as file:
        return part2_elems(file.readlines())

def part2_elems(elems):
    seen = set()
    sum = 0
    for elem in cycle(elems):
        seen.add(sum)
        sum += int(elem)
        if sum in seen:
            return sum

if __name__ == "__main__":
    print("Part1: ", part1("../data/day1-input.txt"))
    print("Part2: ", part2("../data/day1-input.txt"))
