from collections import defaultdict, deque
from itertools import cycle

def calc_part1(nplayers, last_marble):
    scores = defaultdict(int)
    turns = cycle(range(1, nplayers+1))
    marbles = list(range(1, last_marble+1))
    circle = deque([0])
    current = 0
    for marble in marbles:
        player = next(turns)
        if marble % 23 != 0:
            plus1 = (current + 1) % len(circle)
            if plus1 < len(circle) - 1:
                circle.insert(plus1 + 1, marble)
            else:
                circle.append(marble)
            current = plus1 + 1
        else:
            minus7 = (current - 7) % len(circle)
            scores[player] += marble + circle[minus7]
            del circle[minus7]
            current = minus7 % len(circle)
    return max(scores.values())

def test_calc_part1():
    assert 32 == calc_part1(9, 25)
    assert 8317 == calc_part1(10, 1618)
    assert 146373 == calc_part1(13, 7999)
    assert 2764 == calc_part1(17, 1104)
    assert 54718 == calc_part1(21, 6111)
    assert 37305 == calc_part1(30, 5807)

class Node:
    def __init__(self, value=None, prev=None, next=None):
        self.value = value
        self.prev = prev
        self.next = next

class CircularCursor:
    def __init__(self, dll, current):
        self.dll = dll
        self.current = current

    def next(self, steps=1):
        nextCursor = CircularCursor(self.dll, self.current)
        for _ in range(steps):
            nextCursor.current = nextCursor.current.next
            if nextCursor.current.next == nextCursor.dll.last:
                nextCursor.current = nextCursor.dll.first
        return nextCursor

    def prev(self, steps=1):
        prevCursor = CircularCursor(self.dll, self.current)
        for _ in range(steps):
            if prevCursor.current == prevCursor.dll.first:
                prevCursor.current = prevCursor.dll.last.prev
            prevCursor.current = prevCursor.current.prev
        return prevCursor

    def value(self):
        assert self.current != self.dll.last
        return self.current.next.value

    def on_first(self):
        return self.current == self.dll.first

    def on_last(self):
        return self.current.next.next == self.dll.last

    def __eq__(self, other):
        return self.current == other.current

class DoubleLinkedList:
    def __init__(self, iter=None):
        self.first = Node(Node)
        self.last = Node()
        self.first.next = self.last
        self.last.prev = self.first
        self.length = 0
        if iter:
            for elem in iter:
                self.append_right(elem)

    def __len__(self):
        return self.length

    def append_right(self, value):
        newNode = Node(value, prev=self.last.prev, next=self.last)
        self.last.prev.next = newNode
        self.last.prev = newNode
        self.length += 1

    def append_left(self, value):
        newNode = Node(value, prev=self.first, next=self.first.next)
        self.first.next.prev = newNode
        self.first.next = newNode
        self.length += 1

    def insert_after(self, cursor, value):
        newNode = Node(value, prev=cursor.current, next=cursor.current.next)
        cursor.current.next.prev = newNode
        cursor.current.next = newNode
        self.length += 1

    def delete_after(self, cursor):
        oldNode = cursor.current.next
        cursor.current
        cursor.current.next = oldNode.next
        oldNode.next.prev = cursor.current.next
        self.length -= 1

    def to_list(self):
        result = []
        node = self.first.next
        while node != self.last:
            result.append(node.value)
            node = node.next
        return result

    def to_list_reversed(self):
        result = []
        node = self.last.prev
        while node != self.first:
            result.append(node.value)
            node = node.prev
        return result

    def cursor(self):
        return CircularCursor(self, self.first)

def test_cursor_singleton():
    dll = DoubleLinkedList([0])
    cursor = dll.cursor()
    assert 0 == cursor.value()
    assert cursor.on_first()
    assert cursor.on_last()
    assert cursor == cursor.prev()
    assert cursor == cursor.next()

def calc_part2(nplayers, last_marble):
    scores = defaultdict(int)
    turns = cycle(range(1, nplayers+1))
    marbles = list(range(1, last_marble+1))
    #circle = deque([0])
    circle = DoubleLinkedList([0])
    #current = 0
    current = circle.cursor()
    #print("       C: ", current.value(), " L: ", circle.to_list())
    for marble in marbles:
        player = next(turns)
        if marble % 23 != 0:
            plus1 = current.next()
            if not plus1.on_last():
                plus2 = plus1.next()
                circle.insert_after(plus2, marble)
            else:
                circle.append_right(marble)
            current = plus1.next()
        else:
            minus7 = current.prev(7)
            scores[player] += marble + minus7.value()
            circle.delete_after(minus7)
            current = minus7
        #print("P: ", player, " C: ", current.value(), " L: ", circle.to_list())
    return max(scores.values())

def test_calc_part2():
    assert 32 == calc_part2(9, 25)
    assert 8317 == calc_part2(10, 1618)
    assert 146373 == calc_part2(13, 7999)
    assert 2764 == calc_part2(17, 1104)
    assert 54718 == calc_part2(21, 6111)
    assert 37305 == calc_part2(30, 5807)

if __name__ == "__main__":
    print("Part1 ", calc_part1(431, 70950))
    print("Part1 ", calc_part2(431, 70950))
    print("Part2 ", calc_part2(431, 7095000))
