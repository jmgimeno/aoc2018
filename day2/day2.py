from collections import Counter

# Part 1

def part1(fname):
    with open(fname, "r") as boxes:
        return checksum(boxes)
        
def checksum(boxes):
    count2 = count3 = 0
    for box in boxes:
        has2, has3 = check_word(box)
        if has2: 
            count2 += 1
        if has3:
            count3 += 1
    return count2 * count3

def test_checksum():
    boxes = ["abcdef", "bababc", "abbcde", "abcccd", "aabcdd", "abcdee", "ababab"]
    assert 12 == checksum(boxes)

def check_word(word):
    counter = Counter(word)
    values = counter.values()
    return 2 in values, 3 in values

def test_check_word():
    assert (False, False) == check_word("abcdef")
    assert (True, True) == check_word("bababc")
    assert (True, False) == check_word("abbcde")
    assert (False, True) == check_word("abcccd")
    assert (True, False) == check_word("aabcdd")
    assert (True, False) == check_word("abcdee")
    assert (False, True) == check_word("ababab")

# Part 2

def differing_chars(word1, word2):
    assert len(word1) == len(word2)
    accum = []
    for c1, c2 in zip(word1, word2):
        if c1 != c2:
            accum.append((c1, c2))
    return accum

def test_different_chars():
    assert [("b", "x"), ("d", "y")] == differing_chars("abcde", "axcye")
    assert [("h", "u")] == differing_chars("fghij", "fguij")

def common_letters(word1, word2):
    differing = differing_chars(word1, word2)
    assert len(differing) == 1
    (char1, _) = differing[0]
    pos1 = word1.find(char1)
    return word1[0:pos1] + word1[pos1+1:]

def test_common_letters():
    assert "fgij" == common_letters("fghij", "fguij")

def correct_boxes(boxes):
    for idx, box1 in enumerate(boxes):
        for box2 in boxes[idx+1:]:
            differing = differing_chars(box1, box2)
            if len(differing) == 1:
                return box1, box2 # we assume occurs only once

def test_correct_boxes():
    boxes = ["abcde", "fghij", "klmno", "pqrst", "fguij", "axcye", "wvxyz"]
    assert ("fghij", "fguij") == correct_boxes(boxes)

def part2(fname):
    with open(fname, "r") as boxes:
        correct = correct_boxes(boxes.readlines())
        return common_letters(*correct)

if __name__ == "__main__":
    print(part1("input.txt"))
    print(part2("input.txt"))
