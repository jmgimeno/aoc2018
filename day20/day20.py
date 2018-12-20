import collections
import itertools

BEGIN, OPEN, END, CLOSED, TEXT, BAR = 'BEGIN', 'OPEN', 'END', 'CLOSED', 'TEXT', 'BAR'

Seq = collections.namedtuple('Seq', 'elems')
Opt = collections.namedtuple('Opt', 'elems')


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
            yield (CLOSED, level)
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


# regexp  = BEGIN + (body)* + END
# body    = TEXT | OPEN + body + options + CLOSED
# options = (+ BAR + body)+

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


def parse_closed(tokens, idx):
    type_, _ = tokens[idx]
    assert type_ == CLOSED
    return idx + 1, None


def parse_bar(tokens, idx):
    type_, _ = tokens[idx]
    assert type_ == BAR
    return idx + 1, None


def parse_text(tokens, idx):
    type_, text = tokens[idx]
    assert type_ == TEXT
    return idx + 1, text


def parse_options(tokens, idx):
    result = []
    look_ahead, _ = tokens[idx]
    while look_ahead == BAR:
        idx, _ = parse_bar(tokens, idx)
        idx, child = parse_body(tokens, idx)
        result.append(child)
        look_ahead, _ = tokens[idx]
    return idx, result


def parse_body(tokens, idx):
    look_ahead, _ = tokens[idx]
    assert look_ahead in (TEXT, OPEN)
    if look_ahead == TEXT:
        return parse_text(tokens, idx)
    elif look_ahead == OPEN:
        idx, _ = parse_open(tokens, idx)
        idx, first = parse_body(tokens, idx)
        idx, rest = parse_options(tokens, idx)
        idx, _ = parse_closed(tokens, idx)
        return idx, Opt([first] + rest)


def parse_regexp(tokens, idx=0):
    result = []
    idx, _ = parse_begin(tokens, idx)
    look_ahead, _ = tokens[idx]
    while look_ahead != END:
        idx, child = parse_body(tokens, idx)
        result.append(child)
        look_ahead, _ = tokens[idx]
    idx, _ = parse_end(tokens, idx)
    assert idx == len(tokens)
    return Seq(result)


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
                                                         (CLOSED, 2), (CLOSED, 1), (END, None)]


def traverse(tree):
    if isinstance(tree, Seq):
        return sum(traverse(child) for child in tree.elems)
    elif isinstance(tree, Opt):
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
           Seq([Opt(['W', 'N'])])
    assert analyze('^W(N|E)W$') == \
           Seq(['W', Opt(['N', 'E']), 'W'])
    assert analyze('^W(E(N|W)|E)$') == \
           Seq(['W', Opt([Seq(['E', Opt(['N', 'W'])]), 'E'])])
    # assert analyze('^ENWWW(NEEE|SSE(EE|N))$') == \
    #        Seq(['ENWWW', Opt(['NEEE', Seq(['SSE', Opt(['EE', 'N'])])])])


def _test_part1():
    assert part1('^WNE$') == 3
    assert part1('^W(N|E)W$') == 3
    # assert part1('^ENWWW(NEEE|SSE(EE|N))$') == 10
    # assert part1('^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$') == 18
