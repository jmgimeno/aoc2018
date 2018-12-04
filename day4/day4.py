from re import compile

lineRegexp = compile(r"^\[\d+-\d+-\d+ \d+:(\d+)\] (.+)$")
guardRegexp = compile(r"^Guard #(\d+) ")

def most_minutes_guard(data):
    minutes = {}
    for line in sorted(data):
        minute, text = lineRegexp.match(line).groups()
        minute = int(minute)
        matchGuard = guardRegexp.match(text)
        if matchGuard:
            lastGuard = int(matchGuard.group(1))
            minutes.setdefault(lastGuard, 0)
        elif text.startswith("falls"):
            beginSleep = minute
        elif text.startswith("wakes"):
            endSleep = minute
            minutes[lastGuard] += endSleep - beginSleep
    return max(minutes, key=lambda k: minutes[k])

def best_minute(data):
    pass

def part1(data):
    pass

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
    assert 24 == best_minute(test_data)

def test_part1():
    assert 240 == part1(test_data)