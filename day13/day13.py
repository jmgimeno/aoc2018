from collections import namedtuple

# Orientations
UP, RIGHT, DOWN, LEFT = range(4)

# Turning
TURN_LEFT, GO_STRAIGH, TURN_RIGHT = range(3)

def next(turn):
    return (turn + 1) % 3

Cart = namedtuple("Cart", "x, y, orientation, next_turn")

def out_of_lane(cart):
    raise Exception("out of lane", cart)

def horizontal(cart):
    if cart.orientation == RIGHT:
        return cart._replace(x=cart.x+1)
    elif cart.orientation == LEFT:
        return cart._replace(x=cart.x-1)
    else:
        raise Exception("moving %s in horizontal lane", "UP" if cart.orientation == UP else "DOWN")

def vertical(cart):
    if cart.orientation == DOWN:
        return cart._replace(y=cart.y+1)
    elif cart.orientation == UP:
        return cart._replace(y=cart.y-1)
    else:
        raise Exception("moving %s in vertical lane", "LEFT" if cart.orientation == LEFT else "RIGHT")

def diagonal(cart):
    if cart.orientation == UP:
        return cart._replace(y=cart.y-1, orientation=LEFT)
    elif cart.orientation == RIGHT:
        return cart._replace(x=cart.x+1, orientation=DOWN)
    elif cart.orientation == DOWN:
        return cart._replace(y=cart.y+1, orientation=RIGHT)
    else:
        return cart._replace(x=cart.x-1, orientation=UP)

def contra_diagonal(cart):
    if cart.orientation == UP:
        return cart._replace(y=cart.y-1, orientation=RIGHT)
    elif cart.orientation == RIGHT:
        return cart._replace(x=cart.x+1, orientation=UP)
    elif cart.orientation == DOWN:
        return cart._replace(y=cart.y+1, orientation=LEFT)
    else:
        return cart._replace(x=cart.x-1, orientation=DOWN)

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

def crossing(cart):
    orientation = next_orientation[cart.orientation].get(cart.next_turn, cart.orientation)
    next_turn = next(cart.next_turn)
    if cart.orientation == UP:
        return cart._replace(y=cart.y-1, orientation=orientation, next_turn=next_turn)
    elif cart.orientation == RIGHT:
        return cart._replace(x=cart.x+1, orientation=orientation, next_turn=next_turn)
    elif cart.orientation == DOWN:
        return cart._replace(y=cart.y+1, orientation=orientation, next_turn=next_turn)
    else:
        return cart._replace(x=cart.x-1, orientation=orientation, next_turn=next_turn)

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

def parse_carts(lines):
    carts = []
    for y, row in enumerate(lines):
        for x, c in enumerate(row):
            if c in { '>', '<', '^', 'v' }:
                carts.append(Cart(x=x, y=y, orientation=translate_orientation[c], next_turn=0))
    return carts

def test_parse_carts_test1():
    with open("test1.txt", "r") as test1:
        expected = [Cart(x=0, y=1, orientation=DOWN, next_turn=0),
                    Cart(x=0, y=5, orientation=UP, next_turn=0)]
        assert expected == parse_carts(parse_lines(test1))

def test_parse_carts_test2():
    with open("test2.txt", "r") as test2:
        expected = [Cart(x=2, y=0, orientation=RIGHT, next_turn=0),
                    Cart(x=9, y=3, orientation=DOWN, next_turn=0)]
        assert expected == parse_carts(parse_lines(test2))

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
        carts = parse_carts(lines)
        grid = parse_grid(lines)
    return carts, grid

def move(cart, grid):
    if cart.orientation == UP:
        x, y = cart.x, cart.y-1
    elif cart.orientation == RIGHT:
        x, y = cart.x+1, cart.y
    elif cart.orientation == DOWN:
        x, y = cart.x, cart.y+1
    else:
        x, y = cart.x-1, cart.y
    return grid[y][x](cart)

def calc_part1(carts, grid):
    while True:
        carts.sort(key=lambda cart: (cart.y, cart.x))
        occupied_positions = { (cart.x, cart.y) for cart in carts }
        next_carts = []
        for cart in carts:
            occupied_positions.remove((cart.x, cart.y))
            new_cart = move(cart, grid)
            if (new_cart.x, new_cart.y) in occupied_positions:
                return (new_cart.x, new_cart.y)
            occupied_positions.add((new_cart.x, new_cart.y))
            next_carts.append(new_cart)
        carts = next_carts

def part1(fname):
    carts, grid = parse(fname)
    return calc_part1(carts, grid)

def test_part1():
    assert (0, 3) == part1("test1.txt")
    assert (7, 3) == part1("test2.txt")

def calc_part2(carts, grid):
    while True:
        if len(carts) == 1:
            return carts[0].x, carts[0].y
        carts.sort(key=lambda cart: (cart.y, cart.x))
        occupied_positions = { (cart.x, cart.y) for cart in carts }
        next_carts = []
        for cart in carts:
            if (cart.x, cart.y) not in occupied_positions:
                continue
            occupied_positions.remove((cart.x, cart.y))
            new_car = move(cart, grid)
            if (new_car.x, new_car.y) in occupied_positions:
                occupied_positions.remove((new_car.x, new_car.y))
            else:
                occupied_positions.add((new_car.x, new_car.y))
            next_carts.append(new_car)
        carts = [cart for cart in next_carts if (cart.x, cart.y) in occupied_positions]

def part2(fname):
    carts, grid = parse(fname)
    return calc_part2(carts, grid)

def test_part2():
    assert (6, 4) == part2("test3.txt")

if __name__ == "__main__":
    print("Part1", part1("input.txt"))
    print("Part2", part2("input.txt"))
