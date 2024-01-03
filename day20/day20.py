from collections import defaultdict, namedtuple

Leg = namedtuple('Leg', 'start begin end cont_start cont_end')

def mkleg(start, begin, end, cont_start=None, cont_end=None):
    return Leg(start, begin, end, cont_start, cont_end)

class Expedition:

    def __init__(self, regexp):
        self.regexp = regexp
        self.distances = defaultdict(lambda: float('inf'))
        self.doors = set()
        self.legs = {mkleg((1, 1), 0, len(self.regexp))}

    def explore(self):
        assert self.regexp[0] == '^' and self.regexp[-1] == '$'
        counter = 0
        while len(self.legs) > 0:
            next_leg = self.legs.pop()
            self.explore_leg(next_leg)
            counter += 1

    def explore_leg(self, current_leg):
        (x, y) = current_leg.start
        idx = current_leg.begin
        finish = False
        while idx < current_leg.end and not finish:
            old_pos = (x, y)
            current = self.regexp[idx]
            if current == '^':
                self.distances[(x, y)] = 0
            elif current == 'N':
                y -= 2
            elif current == 'E':
                x += 2
            elif current == 'S':
                y += 2
            elif current == 'W':
                x -= 2
            elif current == '$':
                pass
            elif current == '(':
                matching = self.find_matching(idx)
                options = self.find_options(idx, matching)
                for (option_begin, option_end) in options:
                    assert option_begin <= option_end
                    if option_begin < option_end:
                        leg = mkleg((x, y), option_begin, option_end, matching, current_leg.end)
                    else:
                        leg = mkleg((x, y), matching, current_leg.end)
                    self.legs.add(leg)
                finish = True
            elif current == ')':
                pass
            else:
                raise Exception('unexpected character ', current)
            self.distances[(x, y)] = min(1 + self.distances[old_pos], self.distances[(x, y)])
            idx += 1
        if current_leg.cont_start and current_leg.cont_start < current_leg.cont_end:
            leg = mkleg((x, y), current_leg.cont_start, current_leg.cont_end)
            self.legs.add(leg)

    def find_matching(self, idx):
        assert self.regexp[idx] == '('
        opened = 0
        while True:
            idx += 1
            current = self.regexp[idx]
            if current == '(':
                opened += 1
            elif current == ')' and opened == 0:
                return idx + 1
            elif current == ')':
                opened -= 1
            elif current == '^':
                raise Exception("regexp should be well constructed")

    def find_options(self, begin, end):
        assert self.regexp[begin] == '(' and self.regexp[end - 1] == ')'
        options = []
        opened = 0
        option_start = begin + 1
        for idx in range(begin + 1, end):
            current = self.regexp[idx]
            if current == '(':
                opened += 1
            elif current == ')':
                opened -= 1
            elif current == '|' and opened == 0:
                options.append((option_start, idx))
                option_start = idx + 1
            idx += 1
        options.append((option_start, end))
        return options


def part1(regexp):
    expedition = Expedition(regexp)
    expedition.explore()
    return max(expedition.distances.values())

def part2(regexp):
    expedition = Expedition(regexp)
    expedition.explore()
    return sum(1 for v in expedition.distances.values() if v >= 1000)

def test_part1():
    assert part1('^WNE$') == 3
    assert part1('^ENWWW(NEEE|SSE(EE|N))$') == 10
    assert part1('^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$') == 18
    assert part1('^ESSWWN(E|NNENN(EESS(WNSE|)SSS|WWWSSSSE(SW|NNNE)))$') == 23
    assert part1('^WSSEESWWWNW(S|NENNEEEENN(ESSSSW(NWSW|SSEN)|WSWWN(E|WWS(E|SS))))$') == 31


if __name__ == '__main__':
    with open('../data/day20-input.txt', 'r') as file:
        contents = file.read().strip()
        print("Part1: ", part1(contents))
        print("Part2: ", part2(contents))
