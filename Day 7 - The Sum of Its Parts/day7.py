from re import compile

def create_preconditions(data):
    preconditions = {}
    for before, after in data:
        preconditions.setdefault(after, set())
        preconditions.setdefault(before, set())
        preconditions[after].add(before)
    return preconditions

def remove(preconditions, task):
    del preconditions[task]
    for precs in preconditions.values():
        precs.discard(task)

def calc_part1(data):
    preconditions = create_preconditions(data)
    result = ""
    while True:
        realizable = [task for task, precs in preconditions.items() if len(precs) == 0]
        realizable.sort()
        next = realizable[0]
        remove(preconditions, next)
        result += next
        if len(preconditions) == 0: break
    return result

line_regexp = compile(r"^Step (\w+) must be finished before step (\w+) can begin.$")

def parse(line):
    return line_regexp.match(line).groups()

def part1(fname):
    with open(fname, "r") as file:
        return calc_part1([parse(line) for line in file])

test_data = [('C', 'A'), ('C', 'F'), ('A', 'B'), ('A', 'D'), ('B', 'E'), ('D', 'E'), ('F', 'E')]

def test_create_preconditions():
    expected = { 'A' : {'C'}, 'B' : {'A'}, 'C' : set(), 'D' : {'A'}, 'E' : {'B', 'D', 'F'}, 'F' : {'C'}}
    assert expected == create_preconditions(test_data)

def test_calc_part1():
    assert "CABDFE" == calc_part1(test_data)

def test_part1():
    assert "CHILFNMORYKGAQXUVBZPSJWDET" == part1("input.txt")

def calc_part2(data, num_workers, cost_fn):
    preconditions = create_preconditions(data)
    # for each worker what it is working on and when will be free
    # free if no work or current_time >= end_time
    time_table = { w : (None, 0) for w in range(num_workers) }
    ongoing_tasks = set()
    current_time = 0
    result = ""
    while True:
        # Check finished tasks
        finished_tasks = [task for worker, (task, end_time) in time_table.items() if task and current_time == end_time]
        for task in finished_tasks:
            ongoing_tasks.discard(task)
            remove(preconditions, task)
            result += task
        if (len(preconditions)) == 0:
            return current_time, result

        # Update assignments
        available_workers = [worker for worker, (task, end_time) in time_table.items() if not task or current_time >= end_time]
        
        realizable_tasks = [task for task, precs in preconditions.items() if len(precs) == 0 and task not in ongoing_tasks]
        realizable_tasks.sort()

        for worker, task in zip(available_workers, realizable_tasks):
            ongoing_tasks.add(task)
            cost = cost_fn(task)
            time_table[worker] = (task, current_time + cost)

        current_time += 1
    return result

def test_calc_part2():
    assert (15, "CABFDE") == calc_part2(test_data, 2, lambda task: ord(task) - ord('A') + 1)

def part2(fname, num_workers, cost_fn):
    with open(fname, "r") as file:
        return calc_part2([parse(line) for line in file], num_workers, cost_fn)

def test_part2():
    assert (891, 'CINYHLFMRKOGQAXUZPVSBJWDET') == part2("input.txt", 5, lambda task: ord(task) - ord('A') + 61)
if __name__ == "__main__":
    print("Part1: ", part1("input.txt"))
    print("Part2: ", part2("input.txt", 5, lambda task: ord(task) - ord('A') + 61))
