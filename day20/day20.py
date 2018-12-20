import collections


class Walker:

    def __init__(self, x=0, y=0, distances=None):
        self.contexts = []
        self.x = x
        self.y = y
        if not distances:
            self.distances = collections.defaultdict(lambda: float('inf'))
        else:
            self.distances = distances


    def step(self, s):
        current = self.x, self.y
        if s == '^':
            self.contexts.append(current)
            self.distances[current] = 0
        elif s == 'N':
            self.y -= 1
        elif s == 'E':
            self.x += 1
        elif s == 'S':
            self.y += 1
        elif s == 'W':
            self.x -= 1
        elif s == '(':
            self.contexts.append((self.x, self.y))
        elif s == '|':
            self.x, self.y = self.contexts[-1]
        elif s == ')':
            self.contexts.pop()
            self.x, self.y = self.contexts[-1]
        elif s == '$':
            self.contexts.pop()
        else:
            raise Exception('impossible %s' % s)
        self.distances[(self.x, self.y)] = min(1 + self.distances[current], self.distances[(self.x, self.y)])

    def walk(self, steps):
        for s in steps:
            self.step(s)

    def distance_to_farthest(self):
        return max(self.distances.values())


def part1(steps):
    w = Walker()
    w.walk(steps)
    print(w.distances)
    return w.distance_to_farthest()


def test_part1():
    assert part1('^$') == 0
    assert part1('^WNE$') == 3
    assert part1('^ENWWW(NEEE|SSE(EE|N))$') == 10
    # assert part1('^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$') == 18
