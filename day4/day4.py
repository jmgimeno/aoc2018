from re import compile

lineRegexp = compile(r"^\[\d+-\d+-\d+ \d+:(\d+)\] (.+)$")
guardRegexp = compile(r"^Guard #(\d+) ")

def most_minutes_guard(data):
    total_minutes = {}
    for line in data:
        minute, text = lineRegexp.match(line).groups()
        minute = int(minute)
        matchGuard = guardRegexp.match(text)
        if matchGuard:
            lastGuard = int(matchGuard.group(1))
            total_minutes.setdefault(lastGuard, 0)
        elif text.startswith("falls"):
            beginSleep = minute
        elif text.startswith("wakes"):
            endSleep = minute
            total_minutes[lastGuard] += endSleep - beginSleep
    return max(total_minutes, key=lambda k: total_minutes[k])

def best_minute(guard, data):
    minutes = {}
    for line in data:
        minute, text = lineRegexp.match(line).groups()
        minute = int(minute)
        matchGuard = guardRegexp.match(text)
        if matchGuard:
            lastGuard = int(matchGuard.group(1))
        elif guard == lastGuard and text.startswith("falls"):
            beginSleep = minute
        elif guard == lastGuard and text.startswith("wakes"):
            endSleep = minute
            for min in range(beginSleep, endSleep):
                minutes.setdefault(min, 0)
                minutes[min] += 1
    return max(minutes, key=lambda k: minutes[k])

def guard_mult_minutes(data):
    data.sort()
    guard = most_minutes_guard(data)
    minute = best_minute(guard, data)
    return guard * minute

def part1(fname):
    with open(fname, "r") as file:
        return guard_mult_minutes(file.readlines())


def guard_and_minute_most_frequently_sleep(data):
    data.sort()
    counters = {}
    for line in data:
        minute, text = lineRegexp.match(line).groups()
        minute = int(minute)
        matchGuard = guardRegexp.match(text)
        if matchGuard:
            lastGuard = int(matchGuard.group(1))
            counters.setdefault(lastGuard, {})
        elif text.startswith("falls"):
            beginSleep = minute
        elif text.startswith("wakes"):
            endSleep = minute
            for minute in range(beginSleep, endSleep):
                counters[lastGuard].setdefault(minute, 0)
                counters[lastGuard][minute] += 1
    return maxcoordinates(counters)

def maxcoordinates(counters):
    max_freq  = max_guard = max_minute = -1
    for guard, minutes in counters.items():
        for minute, freq in minutes.items():
            if freq > max_freq:
                max_freq = freq
                max_guard = guard
                max_minute = minute
    return max_guard, max_minute

def part2(fname):
    with open(fname, "r") as file:
        guard, minute =  guard_and_minute_most_frequently_sleep(file.readlines())
        return guard * minute

test_data = [
    "[1518-11-01 00:00] Guard #10 begins shift", 
    "[1518-11-01 00:05] falls asleep", 
    "[1518-11-01 00:25] wakes up", 
    "[1518-11-01 00:30] falls asleep", 
    "[1518-11-01 00:55] wakes up", 
    "[1518-11-01 23:58] Guard #99 begins shift", 
    "[1518-11-02 00:40] falls asleep", 
    "[1518-11-02 00:50] wakes up", 
    "[1518-11-03 00:05] Guard #10 begins shift", 
    "[1518-11-03 00:24] falls asleep", 
    "[1518-11-03 00:29] wakes up", 
    "[1518-11-04 00:02] Guard #99 begins shift", 
    "[1518-11-04 00:36] falls asleep", 
    "[1518-11-04 00:46] wakes up", 
    "[1518-11-05 00:03] Guard #99 begins shift", 
    "[1518-11-05 00:45] falls asleep", 
    "[1518-11-05 00:55] wakes up", 
]

def test_most_minutes_guard():
    assert 10 == most_minutes_guard(test_data)

def test_best_minute():
    assert 24 == best_minute(10,test_data)

def test_guard_mult_minutes():
    assert 240 ==guard_mult_minutes(test_data)

def test_part1():
    assert 30630 == part1("../data/day4-input.txt")

def test_guard_most_frequenly_sleep_same_minute():
    assert (99, 45) == guard_and_minute_most_frequently_sleep(test_data)

def test_part2():
    assert 136571 == part2("../data/day4-input.txt")

if __name__ == "__main__":
    print("Part1: ", part1("../data/day4-input.txt"))
    print("Part2: ", part2("../data/day4-input.txt"))