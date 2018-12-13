from collections import namedtuple

# Orientations
UP, RIGHT, DOWN, LEFT = range(4)

# Turning
TURN_LEFT, GO_STRAIGH, TURN_RIGHT = range(3)

def next(turn):
    return (turn + 1) % 3

Car = namedtuple("Car", "x, y, orientation, next_turn")

def out_of_lane(car):
    raise Exception("out of lane", car)

def horizontal(car):
    if car.orientation == RIGHT:
        return car._replace(x=car.x+1)
    elif car.orientation == LEFT:
        return car._replace(x=car.x-1)
    else:
        raise Exception("moving %s in horizontal lane", "UP" if car.orientation == UP else "DOWN")

def vertical(car):
    if car.orientation == DOWN:
        return car._replace(y=car.y+1)
    elif car.orientation == UP:
        return car._replace(y=car.y-1)
    else:
        raise Exception("moving %s in vertical lane", "LEFT" if car.orientation == LEFT else "RIGHT")

def diagonal(car):
    if car.orientation == UP:
        return car._replace(y=car.y-1, orientation=LEFT)
    elif car.orientation == RIGHT:
        return car._replace(x=car.x+1, orientation=DOWN)
    elif car.orientation == DOWN:
        return car._replace(y=car.y+1, orientation=RIGHT)
    else:
        return car._replace(x=car.x-1, orientation=UP)

def contra_diagonal(car):
    if car.orientation == UP:
        return car._replace(y=car.y-1, orientation=RIGHT)
    elif car.orientation == RIGHT:
        return car._replace(x=car.x+1, orientation=UP)
    elif car.orientation == DOWN:
        return car._replace(y=car.y+1, orientation=LEFT)
    else:
        return car._replace(x=car.x-1, orientation=DOWN)

next_orientation = { 
    UP : {
        TURN_LEFT : LEFT,
        TURN_RIGHT : RIGHT }, 
    RIGHT : {
        TURN_LEFT : UP,
        TURN_RIGHT : DOWN }, 
    DOWN : {
        TURN_LEFT : RIGHT,
        TURN_RIGHT : LEFT }, 
    LEFT : {
        TURN_LEFT : DOWN,
        TURN_RIGHT : UP }, 
    }

def crossing(car):
    orientation = next_orientation[car.orientation].get(car.next_turn, car.orientation)
    next_turn = next(car.next_turn)
    if car.orientation == UP:
        return car._replace(y=car.y-1, orientation=orientation, next_turn=next_turn)
    elif car.orientation == RIGHT:
        return car._replace(x=car.x+1, orientation=orientation, next_turn=next_turn)
    elif car.orientation == DOWN:
        return car._replace(y=car.y+1, orientation=orientation, next_turn=next_turn)
    else:
        return car._replace(x=car.x-1, orientation=orientation, next_turn=next_turn)

translate_orientation = { "^" : UP, ">" : RIGHT, "v" : DOWN, "<" : LEFT }

translate_cell = { " " : out_of_lane, 
                   "-" : horizontal, "<" : horizontal, ">" : horizontal,
                   "|" : vertical, "^" : vertical, "v" : vertical,
                   "/" : contra_diagonal, 
                   "\\" : diagonal,
                   "+" : crossing }

def parse_lines(file):
    return [line.rstrip("\n") for line in file if len(line) > 0]

def test_parse_lines_test1():
    with open("test1.txt", "r") as test1:
        expected = ['|', 'v', '|', '|', '|', '^', '|']
        assert expected == parse_lines(test1)

def test_parse_lines_test2():
    with open("test2.txt", "r") as test2:
        expected = ['/->-\\        ',
                    '|   |  /----\\',
                    '| /-+--+-\\  |',
                    '| | |  | v  |',
                    '\\-+-/  \\-+--/',
                    '  \\------/   ']
        assert expected == parse_lines(test2)

def parse_cars(lines):
    cars = []
    for y, row in enumerate(lines):
        for x, c in enumerate(row):
            if c in { '>', '<', '^', 'v' }:
                cars.append(Car(x=x, y=y, orientation=translate_orientation[c], next_turn=0))
    return cars

def test_parse_cars_test1():
    with open("test1.txt", "r") as test1:
        expected = [Car(x=0, y=1, orientation=DOWN, next_turn=0),
                    Car(x=0, y=5, orientation=UP, next_turn=0)]
        assert expected == parse_cars(parse_lines(test1))

def test_parse_cars_test2():
    with open("test2.txt", "r") as test2:
        expected = [Car(x=2, y=0, orientation=RIGHT, next_turn=0),
                    Car(x=9, y=3, orientation=DOWN, next_turn=0)]
        assert expected == parse_cars(parse_lines(test2))

def parse_grid(lines):
    grid = []
    for line in lines:
        row = []
        for c in line:
            row.append(translate_cell[c])
        grid.append(row)
    return grid

def test_parse_grid_test1():
    with open("test1.txt", "r") as test1:
        expected = [[vertical]] * 7
        assert expected == parse_grid(parse_lines(test1))

def parse(fname):
    with open(fname, "r") as f:
        lines = parse_lines(f)
        cars = parse_cars(lines)
        grid = parse_grid(lines)
    return cars, grid

def move(car, grid):
    if car.orientation == UP:
        x, y = car.x, car.y-1
    elif car.orientation == RIGHT:
        x, y = car.x+1, car.y
    elif car.orientation == DOWN:
        x, y = car.x, car.y+1
    else:
        x, y = car.x-1, car.y
    return grid[y][x](car)

def simulate(cars, grid):
    tick = 0
    while True:
        cars.sort(key=lambda car: (car.y, car.x))
        positions = { (car.x, car.y) for car in cars }
        next_cars = []
        for car in cars:
            positions.remove((car.x, car.y))
            new_car = move(car, grid)
            if (new_car.x, new_car.y) in positions:
                return (new_car.x, new_car.y)
            positions.add((new_car.x, new_car.y))
            next_cars.append(new_car)
        cars = next_cars
        tick += 1

def test_simulate_test1():
    cars, grid = parse("test1.txt")
    assert (0, 3) == simulate(cars, grid)

def test_simulate_test2():
    cars, grid = parse("test2.txt")
    assert (7, 3) == simulate(cars, grid)

def part1(fname):
    cars, grid = parse(fname)
    return simulate(cars, grid)

if __name__ == "__main__":
    print("Part1", part1("input.txt"))
