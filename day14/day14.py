class Scoreboard:

    def __init__(self, recipe0, recipe1):
        self.recipes = [recipe0, recipe1]
        self.elf0 = 0
        self.elf1 = 1

    def __repr__(self):
        accum = []
        for idx, recipe in enumerate(self.recipes):
            if idx == self.elf0:
                accum.append("(%d)" % recipe)
            elif idx == self.elf1:
                accum.append("[%d]" % recipe)
            else:
                accum.append(" %d " % recipe)
        return "".join(accum)

    def __getitem__(self, idx):
        return self.recipes[idx]

    def __len__(self):
        return len(self.recipes)

    def step(self, num=1):
        for _ in range(num):
            recipe0 = self.recipes[self.elf0]
            recipe1 = self.recipes[self.elf1]
            sum_recipes = recipe0 + recipe1
            if sum_recipes > 9:
                self.recipes.append(sum_recipes // 10)
            self.recipes.append(sum_recipes % 10)
            self.elf0 = (self.elf0 + recipe0 + 1 ) % len(self.recipes)
            self.elf1 = (self.elf1 + recipe1 + 1 ) % len(self.recipes)

def part1(number):
    scoreboard = Scoreboard(3, 7)
    while len(scoreboard) < number + 12:
        scoreboard.step()
    return "".join(map(str, scoreboard[number:number+10]))

def part2(pattern):
    scoreboard = Scoreboard(3, 7)
    lpattern = [int(r) for r in pattern]
    while scoreboard[-6:-1] != lpattern and scoreboard[-5:] != lpattern:
        scoreboard.step()
    return len(scoreboard) - 5

def test_create_scoreboar():
    s = Scoreboard(3, 7)
    assert "(3)[7]" == repr(s)

def test_1step():
    s = Scoreboard(3, 7)
    s.step()
    assert "(3)[7] 1  0 " == repr(s)

def test_2steps():
    s = Scoreboard(3, 7)
    s.step(2)
    assert " 3  7  1 [0](1) 0 " == repr(s)

def test_15steps():
    s = Scoreboard(3, 7)
    s.step(15)
    assert " 3  7  1  0 [1] 0  1  2 (4) 5  1  5  8  9  1  6  7  7  9  2 " == repr(s)

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

# Generators

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
        yield recipes
        elf0 = (elf0 + recipe0 + 1 ) % len(recipes)
        elf1 = (elf1 + recipe1 + 1 ) % len(recipes)

def part1gen(number):
    scoreboard_gen = scoreboards(3, 7)
    scoreboard = next(scoreboard_gen)
    while len(scoreboard) < number + 12:
        scoreboard = next(scoreboard_gen)
    return "".join(map(str, scoreboard[number:number+10]))

def part2gen(pattern):
    lpattern = [int(r) for r in pattern]
    for scoreboard in scoreboards(3, 7):
        if scoreboard[-5:] == lpattern:
            break
        if len(scoreboard) % 100_000 == 0:
            print(len(scoreboard), scoreboard[-5:])
    return len(scoreboard) - 5

def test_part1gen():
    assert "0124515891" == part1gen(5)
    assert "5158916779" == part1gen(9)
    assert "9251071085" == part1gen(18)
    assert "5941429882" == part1gen(2018)

def test_part2gen():
    assert 5 == part2gen("01245")
    assert 9 == part2gen("51589")
    assert 18 == part2gen("92510")
    assert 2018 == part2gen("59414")

if __name__ == "__main__":
    print("Part1: ", part1(30121))
    print("Part1: ", part1gen(30121))
    # solution is 20287556
    #print("Part2: ", part2gen("030121"))
