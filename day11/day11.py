import itertools
import numpy

N = 300

def power_level_fn(serial_number):
    def power_of_cell(x, y):
        # x and y begining at 1
        rackID = x + 10
        power = rackID * y
        power += serial_number
        power *= rackID
        hundreds = (power // 100) % 10
        return hundreds - 5
    return power_of_cell

def test_level_fn():
    assert 4 == power_level_fn(8)(3, 5)
    assert -5 == power_level_fn(57)(122, 79)
    assert 0 == power_level_fn(39)(217, 196)
    assert 4 == power_level_fn(71)(101, 153)

def init_grid(serial_number):
    power_fn = power_level_fn(serial_number)
    return numpy.fromfunction(lambda i, j: power_fn(j+1, i+1), (N, N), dtype=int)

def subgrid(grid, x, y, size):
    return grid[y-1:y-1+size, x-1:x-1+size]

def test_init_grid():
    expected = numpy.array([[-2, -4, 4,  4,  4],
                            [-4,  4, 4,  4, -5],
                            [ 4,  3, 3,  4, -4],
                            [ 1,  1, 2,  4, -3],
                            [-1,  0, 2, -5, -2]])
    grid = init_grid(18)
    # (x, y) = (32, 44)
    actual = subgrid(grid, 32, 44, 5)
    assert numpy.array_equal(expected, actual)

def part1(serial_number):
    grid = init_grid(serial_number)
    return best_of_size(grid, 3)

def best_of_size(grid, size):
    max_sum = float("-inf")
    for x, y in itertools.product(range(1, N+2-size), range(1, N+2-size)):
        current_subgrid = subgrid(grid, x, y, size)
        current_sum = numpy.sum(current_subgrid)
        if current_sum > max_sum:
            max_sum = current_sum
            max_xy = x, y
            max_subgrid = current_subgrid
    return max_xy, max_sum, max_subgrid 

def part2(serial_number):
    grid = init_grid(serial_number)
    max_sum = float("-inf")
    for size in range(1, N+1):
        current_xy, current_sum, current_subgrid = best_of_size(grid, size)
        if current_sum > max_sum:
            max_sum = current_sum
            max_xy = current_xy
            max_subgrid = current_subgrid
            max_size = size
    return max_xy, max_size, max_sum, max_subgrid

def _part2(serial_number):
    grid = init_grid(serial_number)
    size = max_size = 1
    max_xy, max_sum, max_subgrid = best_of_size(grid, max_size)
    while True:
        size += 1
        current_xy, current_sum, current_subgrid = best_of_size(grid, size)
        if current_sum > max_sum:
            max_xy = current_xy
            max_sum = current_sum
            max_subgrid = current_subgrid
            max_size = size
        else:
            break
    return max_xy, max_size, max_sum, max_subgrid         

def test_part1_on_grid18():
    expected = numpy.array([[4, 4, 4],
                            [3, 3, 4],
                            [1, 2, 4]])
    xy, max_sum, max_subgrid = part1(18)
    assert xy == (33, 45)
    assert max_sum == 29
    assert numpy.array_equal(expected, max_subgrid)

def test_part1_on_grid42():
    expected = numpy.array([[4, 3, 3],
                            [3, 3, 4],
                            [3, 3, 4]])
    xy, max_sum, max_subgrid = part1(42)
    assert xy == (21, 61)
    assert max_sum == 30
    assert numpy.array_equal(expected, max_subgrid)

def test_part2_on_grid18():
    xy, size, max_sum, _ = part2(18)
    assert (90, 269) == xy
    assert 16 == size
    assert 113 == max_sum

def test_part2_on_grid42():
    xy, size, max_sum, _ = part2(42)
    assert (232, 251) == xy
    assert 12 == size
    assert 119 == max_sum

if __name__ == "__main__":
    print(part1(6392))
    print(part2(6392))
