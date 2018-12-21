from collections import defaultdict


class Leg:

    def __init__(self, start, begin, end, cont_start=None, cont_end=None):
        self.start = start
        self.begin = begin
        self.end = end
        self.cont_start = cont_start
        self.cont_end = cont_end

    def __repr__(self):
        fmt = "Leg(start={start} begin={begin} end={end} cont_start={cont_start} cont_end={cont_end})"
        return fmt.format(**self.__dict__)


class Expedition:

    def __init__(self, regexp):
        self.regexp = regexp
        self.distances = defaultdict(lambda: float('inf'))
        self.doors = set()
        self.legs = [Leg((1, 1), 0, len(self.regexp))]

    def explore(self):
        counter = 0
        while len(self.legs) > 0:
            next_leg = self.legs.pop()
            # print("Current leg", next_leg)
            self.explore_leg(next_leg)
            if counter % 100000 == 0:
                print("Iteration {} Legs {}".format(counter, len(self.legs)))
                # print(self.legs)
            counter += 1

    def explore_leg(self, next_leg):
        (x, y) = next_leg.start
        idx = next_leg.begin
        finish = False
        while idx < next_leg.end and not finish:
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
                matching = self.find_matching(idx + 1)
                options = self.find_options(idx + 1, matching)
                # print(idx, matching, options)
                for (option_begin, option_end) in options:
                    leg = Leg((x, y), option_begin, option_end, matching + 1, next_leg.end)
                    # print("Added leg", leg)
                    self.legs.append(leg)
                finish = True
            self.distances[(x, y)] = min(1 + self.distances[old_pos], self.distances[(x, y)])
            idx += 1
        if next_leg.cont_start:
            leg = Leg((x, y), next_leg.cont_start, next_leg.cont_end)
            self.legs.append(leg)

    def find_matching(self, idx):
        opened = 0
        while True:
            current = self.regexp[idx]
            if current == '(':
                opened += 1
            elif current == ')' and opened == 0:
                return idx
            elif current == ')':
                opened -= 1
            elif current == '^':
                raise Exception("regexp shoul be well constructed")
            idx += 1

    def find_options(self, begin, end):
        options = []
        opened = 0
        option_start = begin
        for idx in range(begin, end + 1):
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


def test_part1():
    assert part1('^WNE$') == 3
    assert part1('^ENWWW(NEEE|SSE(EE|N))$') == 10
    assert part1('^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$') == 18
    assert part1('^ESSWWN(E|NNENN(EESS(WNSE|)SSS|WWWSSSSE(SW|NNNE)))$') == 23
    assert part1('^WSSEESWWWNW(S|NENNEEEENN(ESSSSW(NWSW|SSEN)|WSWWN(E|WWS(E|SS))))$') == 31


if __name__ == '__main__':
    with open('input.txt', 'r') as file:
        regexp = file.read()
        print("Regexp length: ", len(regexp))
        print("Part1: ", part1(regexp))
