import collections
import copy
import operator

Op = collections.namedtuple('Op', 'opcode a b c')
Sample = collections.namedtuple('Sample', 'before op after')


def make_rr(operator):
    def opcode(op, input):
        output = input[:]
        output[op.c] = operator(
            input[op.a], input[op.b])
        return output
    return opcode


def make_ri(operator):
    def opcode(op, input):
        output = input[:]
        output[op.c] = operator(input[op.a], op.b)
        return output
    return opcode


def make_ir(operator):
    def opcode(op, input):
        output = input[:]
        output[op.c] = operator(op.a, input[op.b])
        return output
    return opcode


addr = make_rr(operator.add)
addi = make_ri(operator.add)

mulr = make_rr(operator.mul)
muli = make_ri(operator.mul)

banr = make_rr(operator.and_)
bani = make_ri(operator.and_)

borr = make_rr(operator.or_,)
bori = make_ri(operator.or_,)


def setr(op, input):
    output = input[:]
    output[op.c] = input[op.a]
    return output


def seti(op, input):
    output = input[:]
    output[op.c] = op.a
    return output


gtir = make_ir(lambda arg1, arg2: 1 if arg1 > arg2 else 0)
gtri = make_ri(lambda arg1, arg2: 1 if arg1 > arg2 else 0)
gtrr = make_rr(lambda arg1, arg2: 1 if arg1 > arg2 else 0)

eqir = make_ir(lambda arg1, arg2: 1 if arg1 == arg2 else 0)
eqri = make_ri(lambda arg1, arg2: 1 if arg1 == arg2 else 0)
eqrr = make_rr(lambda arg1, arg2: 1 if arg1 == arg2 else 0)

OPS = {addr, addi, mulr, muli, banr, bani, borr, bori,
       setr, seti, gtir, gtri, gtrr, eqir, eqri, eqrr}


def compatible_ops(sample):
    return {op_fn for op_fn in OPS if op_fn(sample.op, sample.before) == sample.after}


def test_ops():
    assert [0, 10, 20, 10 + 20] == addr(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 10 + 2] == addi(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 10 * 20] == mulr(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 10 * 2] == muli(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 10 & 20] == banr(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 10 & 2] == bani(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 10 | 20] == borr(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 10 | 2] == bori(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 10] == setr(Op(
        opcode=None, a=1, b=None, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 1] == seti(Op(
        opcode=None, a=1, b=None, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 0] == gtir(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 1] == gtri(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 0] == gtrr(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 0] == eqir(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 0] == eqri(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])
    assert [0, 10, 20, 0] == eqrr(Op(
        opcode=None, a=1, b=2, c=3), [0, 10, 20, 40])


def test_compatible_ops():
    assert {mulr, addi, seti} == compatible_ops(
        Sample(before=[3, 2, 1, 1], op=Op(9, 2, 1, 2), after=[3, 2, 2, 1]))


class Parser():
    def __init__(self, fname):
        self.fname = fname

    def parse_samples(self, file):
        samples = []
        while True:
            line = file.readline().strip()
            if not line:
                return samples
            before = eval(line[8:])
            line = file.readline().strip()
            op = Op(*(int(s) for s in line.split()))
            line = file.readline().strip()
            after = eval(line[8:])
            samples.append(Sample(before=before, op=op, after=after))
            file.readline()

    def parse_program(self, file):
        return [Op(*(int(s) for s in line.strip().split())) for line in file]

    def parse(self):
        with open(self.fname, 'r') as file:
            samples = self.parse_samples(file)
            file.readline()
            program = self.parse_program(file)
            return samples, program


def part1(fname):
    samples, _ = Parser('../data/day16-input.txt').parse()
    return sum(1 for sample in samples if len(compatible_ops(sample)) >= 3)


def compatibility_table(samples):
    table = collections.defaultdict(set)
    for sample in samples:
        table[sample.op.opcode].update(compatible_ops(sample))
    return table


def propagate(table):
    remaining = copy.deepcopy(table)
    assignments = {}
    while True:
        ones = {opcode: ops.pop() for opcode, ops in remaining.items()
                if len(ops) == 1 and opcode not in assignments}
        if len(ones) == 0:
            return assignments, remaining
        for opcode in list(remaining.keys()):
            remaining[opcode] -= set(ones.values())
            if len(remaining[opcode]) == 0:
                del remaining[opcode]
        assignments.update(ones)


def run(program, assignments):
    register = [0] * 4
    for op in program:
        op_fn = assignments[op.opcode]
        register = op_fn(op, register)
    return register


def part2(fname):
    samples, program = Parser('../data/day16-input.txt').parse()
    ct = compatibility_table(samples)
    assignments, remaining = propagate(ct)
    assert len(remaining) == 0
    register = run(program, assignments)
    return register[0]


if __name__ == '__main__':
    print('Part1:', part1('../data/day16-input.txt'))
    print('Part2:', part2('../data/day16-input.txt'))
