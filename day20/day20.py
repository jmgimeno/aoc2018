import collections
import itertools

# Lexer

BEGIN, OPEN, END, CLOSE, TEXT, BAR = 'BEGIN', 'OPEN', 'END', 'CLOSE', 'TEXT', 'BAR'


def tokenize(regex):
    idx = 0
    level = 0
    while idx < len(regex):
        if regex[idx] == '^':
            yield (BEGIN, None)
            idx += 1
        elif regex[idx] == '$':
            yield (END, None)
            idx += 1
        elif regex[idx] == '(':
            level += 1
            yield (OPEN, level)
            idx += 1
        elif regex[idx] == ')':
            yield (CLOSE, level)
            level -= 1
            idx += 1
        elif regex[idx] == '|' and regex[idx + 1] == '|':  # Simplifies parser
            yield (BAR,)
            yield (TEXT, '')
            idx += 1
        elif regex[idx] == '|' and regex[idx + 1] == ')':  # Simplifies parser
            yield (BAR,)
            yield (TEXT, '')
            idx += 1
        elif regex[idx] == '|':
            yield (BAR, None)
            idx += 1
        else:
            length = sum(1 for _ in itertools.takewhile(str.isalpha, (c for c in regex[idx:])))
            yield (TEXT, regex[idx:idx + length])
            idx += length


# Parser

Seq = collections.namedtuple('Seq', 'elems')
Alt = collections.namedtuple('Alt', 'elems')


# regexp      = BEGIN + sequence + END
# sequence    = (TEXT | OPEN + alternative + CLOSE)*
# alternative = sequence | (BAR + sequence)*

def parse_begin(tokens, idx):
    type_, _ = tokens[idx]
    assert type_ == BEGIN
    return idx + 1, None


def parse_end(tokens, idx):
    type_, _ = tokens[idx]
    assert type_ == END
    return idx + 1, None


def parse_open(tokens, idx):
    type_, _ = tokens[idx]
    assert type_ == OPEN
    return idx + 1, None


def parse_close(tokens, idx):
    type_, _ = tokens[idx]
    assert type_ == CLOSE
    return idx + 1, None


def parse_bar(tokens, idx):
    type_, _ = tokens[idx]
    assert type_ == BAR
    return idx + 1, None


def parse_text(tokens, idx):
    type_, text = tokens[idx]
    assert type_ == TEXT
    return idx + 1, text


def parse_regexp(tokens, idx=0):
    idx, _ = parse_begin(tokens, idx)
    idx, seq = parse_sequence(tokens, idx)
    idx, _ = parse_end(tokens, idx)
    assert idx == len(tokens)
    return seq


def parse_sequence(tokens, idx):
    elems = []
    look_ahead, _ = tokens[idx]
    while look_ahead in (TEXT, OPEN):
        if look_ahead == TEXT:
            idx, text = parse_text(tokens, idx)
            elems.append(text)
        elif look_ahead == OPEN:
            idx, _ = parse_open(tokens, idx)
            idx, alt = parse_alternative(tokens, idx)
            idx, _ = parse_close(tokens, idx)
            elems.append(alt)
        look_ahead, _ = tokens[idx]
    return idx, Seq(elems)



def parse_alternative(tokens, idx):
    elems = []
    look_ahead, _ = tokens[idx]
    while look_ahead != CLOSE:
        if look_ahead == BAR:
            idx, _ = parse_bar(tokens, idx)
        look_ahead, _ = tokens[idx]
        idx, elem = parse_sequence(tokens, idx)
        elems.append(elem)
        look_ahead, _ = tokens[idx]
    return idx, Alt(elems)


def analyze(regexp):
    tokens = list(tokenize(regexp))
    return parse_regexp(tokens)


def test_tokenize():
    assert list(tokenize('^$')) == [(BEGIN, None), (END, None)]
    assert list(tokenize('^WNE$')) == [(BEGIN, None), (TEXT, 'WNE'), (END, None)]
    assert list(tokenize('^ENWWW(NEEE|SSE(EE|N))$')) == [(BEGIN, None), (TEXT, 'ENWWW'), (OPEN, 1), (TEXT, 'NEEE'),
                                                         (BAR, None),
                                                         (TEXT, 'SSE'), (OPEN, 2), (TEXT, 'EE'), (BAR, None),
                                                         (TEXT, 'N'),
                                                         (CLOSE, 2), (CLOSE, 1), (END, None)]


def traverse(tree):
    if isinstance(tree, Seq):
        return sum(traverse(child) for child in tree.elems)
    elif isinstance(tree, Alt):
        return max(traverse(child) for child in tree.elems)
    else:
        return len(tree)


def part1(regexp):
    tokens = list(tokenize(regexp))
    tree = parse_regexp(tokens)
    return traverse(tree)


def test_analyze():
    assert analyze('^$') == \
           Seq([])
    assert analyze('^WN$') == \
           Seq(['WN'])
    assert analyze('^(W|N)$') == \
           Seq([Alt(['W', 'N'])])
    # assert analyze('^W(N|E)W$') == \
    #        Seq(['W', Alt(['N', 'E']), 'W'])
    # # print(analyze('^W(E(N|W)|E)$'))
    # assert analyze('^W(E(N|W)|E)$') == \
    #        Seq(['W', Alt([Seq(['E', Alt(['N', 'W'])]), 'E'])])
    # # assert analyze('^ENWWW(NEEE|SSE(EE|N))$') == \
    #        Seq(['ENWWW', Opt(['NEEE', Seq(['SSE', Opt(['EE', 'N'])])])])


def test_part1():
    assert part1('^WNE$') == 3
    assert part1('^W(N|E)W$') == 3
    assert part1('^ENWWW(NEEE|SSE(EE|N))$') == 10
    assert part1('^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$') == 18
