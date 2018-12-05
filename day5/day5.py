def reacts(mer1, mer2):
    return mer1.islower() != mer2.islower() and mer1.lower() == mer2.lower()

def test_reacts():
    assert reacts("a", "A")
    assert reacts("A", "a")
    assert not reacts("a", "a")
    assert not reacts("A", "A")
    assert not reacts("a", "B")

def reaction_step(polymer):
    to_remove = set()
    idx = 0
    while idx < len(polymer) - 1:
        if reacts(polymer[idx], polymer[idx+1]):
            to_remove.update({idx, idx+1})
            idx += 1
        idx += 1
    return "".join(mer for (idx, mer) in enumerate(polymer) if idx not in to_remove)

def test_reaction_step():
    assert "" == reaction_step("aA")
    assert "dabCBAcaDA" == reaction_step("dabCBAcaDA")
    assert "dabCBAcaDA" == reaction_step("dabCBAcCcaDA")

def full_reaction(polymer):
    while True:
        transformed = reaction_step(polymer)
        if transformed == polymer:
            break
        polymer = transformed
    return polymer

def test_full_reaction():
    assert "" == full_reaction("aA")
    assert "" == full_reaction("abBA")
    assert "dabCBAcaDA" == full_reaction("dabCBAcaDA")
    assert "dabCBAcaDA" == full_reaction("dabCBAcCcaDA")
    assert "dabCBAcaDA" == full_reaction("dabAaCBAcCcaDA")
    assert "dabCBAcaDA" == full_reaction("dabAcCaCBAcCcaDA")

def part1(fname):
    with open(fname, "r") as file:
        # Had to remove tha last char (newline?)
        return len(full_reaction(file.read()[:-1]))

def test_part1():
    assert 11108 == part1("input.txt")

if __name__ == "__main__":
    print("Part1: ", part1("input.txt"))