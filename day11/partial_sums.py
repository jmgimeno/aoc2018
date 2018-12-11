def main():
    serial = int(input())
    sz = 300
    grid = [[0 for _ in range(sz + 1)] for _ in range(sz + 1)]

    for x in range(1, sz + 1):
        for y in range(1, sz + 1):
            cost = x * x * y + 20 * x * y + (x + 10) * serial + 100 * y
            cost //= 100
            cost %= 10
            cost -= 5
            grid[x][y] = cost

    # 2d prefix sums of the grid
    for x in range(1, sz + 1):
        for y in range(1, sz + 1):
            grid[x][y] = grid[x][y] + grid[x - 1][y] + grid[x][y - 1] - grid[x - 1][y - 1]

    ans =  (0, (0, 0))
    #for blk in range(3, 4):
    for blk in range(1, sz):
        for x in range(1, sz - blk + 1):
            for y in range(1, sz - blk + 1):
                tot = grid[x + blk][y + blk] - grid[x][y + blk] - grid[x + blk][y] + grid[x][y]

                ans = max(ans, (tot, (x + 1, y + 1, blk)))

    print(ans)

main()