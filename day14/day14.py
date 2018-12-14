def scoreboards(recipe0, recipe1):
    recipes = [recipe0, recipe1]
    elf0 = 0
    elf1 = 1
    yield recipes
    while True:
        recipe0 = recipes[elf0]
        recipe1 = recipes[elf1]
        sum_recipes = recipe0 + recipe1
        if sum_recipes > 9:
            recipes.append(sum_recipes // 10)
            yield recipes
        recipes.append(sum_recipes % 10)
        elf0 = (elf0 + recipe0 + 1 ) % len(recipes)
        elf1 = (elf1 + recipe1 + 1 ) % len(recipes)
        yield recipes

def part1(number):
    scoreboard_gen = scoreboards(3, 7)
    scoreboard = next(scoreboard_gen)
    while len(scoreboard) < number + 12:
        scoreboard = next(scoreboard_gen)
    return "".join(map(str, scoreboard[number:number+10]))

def part2(pattern):
    lpattern = [int(r) for r in pattern]
    for scoreboard in scoreboards(3, 7):
        if scoreboard[-len(pattern):] == lpattern:
            break
    return len(scoreboard) - len(pattern)

def test_part1():
    assert "0124515891" == part1(5)
    assert "5158916779" == part1(9)
    assert "9251071085" == part1(18)
    assert "5941429882" == part1(2018)

def test_part2():
    assert 5 == part2("01245")
    assert 9 == part2("51589")
    assert 18 == part2("92510")
    assert 2018 == part2("59414")

if __name__ == "__main__":
    print("Part1:   ", part1(30121))
    print("Part2:   ", part2("030121"))
