from re import compile

line_regexp = compile(r"^position=<\s*(\-?\d+),\s*(\-?\d+)> velocity=<\s*(\-?\d+),\s*(\-?\d+)>$")

def parse(line):
    x, y, vx, vy = map(int, line_regexp.match(line).groups())
    return (x, y), (vx, vy)

def add(v1, v2):
    return v1[0]+v2[0], v1[1]+v2[1]

def distance(v1, v2):
    return abs(v1[0]-v2[0]) + abs(v1[1]-v2[1])

def total_distance(positions):
    total = 0
    for idx, v1 in enumerate(positions):
        for v2 in positions[idx+1:]:
            total += distance(v1, v2)
    return total

def step(positions, velocities):
    return [add(p, v) for p, v in zip(positions, velocities)]

def calc_min(positions_0, velocities):
    total_0 = total_distance(positions_0)
    positions_1 = step(positions_0, velocities)
    total_1 = total_distance(positions_1)
    positions_2 = step(positions_1, velocities)
    total_2 = total_distance(positions_2)
    time = 1
    while not (total_0 >= total_1 and total_1 <= total_2):
        total_0, total_1 = total_1, total_2
        positions_0, positions_1 = positions_1, positions_2
        positions_2 = step(positions_1, velocities)
        total_2 = total_distance(positions_2)
        time += 1
    return time, positions_1

def show(positions):
    x_min = min(p[0] for p in positions)
    x_max = max(p[0] for p in positions)
    y_min = min(p[1] for p in positions)
    y_max = max(p[1] for p in positions)
    width, height = x_max-x_min+1, y_max-y_min+1
    grid = [['·'] * width for _ in range(height)]
    for x, y in positions:
        grid[y-y_min][x-x_min] = '#'
    return "\n".join("".join(xy for xy in row) for row in grid)

def calc_part1(lines):
    positions = [line[0] for line in lines]
    velocities = [line[1] for line in lines]
    time, min_position = calc_min(positions, velocities)
    return time, show(min_position)

def part1(fname):
    with open(fname, 'r') as file:
        time, image = calc_part1([parse(line) for line in file])
        print(time)
        print(image)

if __name__ == "__main__":
    part1("test_input.txt")
    #part1("input.txt")
