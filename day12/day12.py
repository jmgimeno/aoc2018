from collections import namedtuple
from itertools import takewhile

State = namedtuple("State", ["first", "plants", "generation"])

def normalize(state):
    first_plant = 0
    for c in state.plants:
        if c == "#":
            break
        first_plant += 1
    last_plant = len(state.plants)
    for c in reversed(state.plants):
        if c == "#":
            break
        last_plant -= 1
    plants = "..." + state.plants[first_plant:last_plant] + "..."
    first = state.first + first_plant - 3
    return State(first, plants, state.generation)

def test_normalize():
    expected_state = State(-3, "...#...#....#.....#..#..#..#...", 0)
    state = State(0, "#...#....#.....#..#..#..#", 0)
    assert expected_state == normalize(state)

def step(state, rules):
    next_plants = ".."
    for idx in range(len(state.plants) - 4):
        current = state.plants[idx:idx+5]
        next_plants += rules.get(current, ".")
    return normalize(State(state.first, next_plants, state.generation+1))

def test_step():
    expected_state = State(-3, "...#...#....#.....#..#..#..#...", 1)
    with open("test_input.txt", "r") as file:
        initial_state, rules = process(file) 
        actual_state = step(initial_state, rules)
        assert expected_state == actual_state

def simulate(state, rules, num_generations):
    seen_states = { state.plants : (state, 0) }
    while state.generation < num_generations:
        new_state = step(state, rules)
        if new_state.plants in seen_states:
            period = new_state.generation - seen_states[state.plants].generation
            delta = new_state.first - seen_states[state.plants].first
            remaining = num_generations - new_state.generation
            repetitions = remaining // period
            state = State(
                new_state.first + delta * repetitions, 
                new_state.plants, 
                new_state.generation + repetitions * period)
            seen_states = {}
        else:    
            state = seen_states[state.plants] = new_state
    return state

def sum_plant_positions(state):
    result = 0
    pos = state.first
    for plant in state.plants:
        if plant == "#":
            result += pos
        pos += 1
    return result

def process(file):
    line = file.readline()
    initial_state = normalize(State(0, line[len("initial state: "):].strip(), 0))
    file.readline()
    rules = dict(parse_rule(line.strip()) for line in file)
    return initial_state, rules

def parse_rule(line):
    return line[:5], line[-1:]

def test_process():
    expected_state = State(-3, "...#..#.#..##......###...###...", 0)
    expected_rules = { "...##" : "#",
                       "..#.." : "#",
                       ".#..." : "#",
                       ".#.#." : "#",
                       ".#.##" : "#",
                       ".##.." : "#",
                       ".####" : "#",
                       "#.#.#" : "#",
                       "#.###" : "#",
                       "##.#." : "#",
                       "##.##" : "#",
                       "###.." : "#",
                       "###.#" : "#",
                       "####." : "#"  }

    with open("test_input.txt", "r") as file:
        actual_state, actual_rules = process(file)
        assert expected_state == actual_state
        assert expected_rules == actual_rules

def part1(fname, num_generations):
    with open(fname, "r") as file:
        initial_state, rules = process(file)
        end_state = simulate(initial_state, rules, num_generations)
        return sum_plant_positions(end_state)

def test_part1():
    assert 325 == part1("test_input.txt", 20)

if __name__ == "__main__":
    print("Part1: ", part1("input.txt", 20))
    print("Part2: ", part1("input.txt", 50000000000))
