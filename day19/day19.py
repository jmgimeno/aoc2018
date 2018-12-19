import collections
import operator

# Operations copied from day16

Op = collections.namedtuple('Op', 'opname a b c')


def make_rr(operator_):
    def opcode(op, input_):
        output = input_[:]
        output[op.c] = operator_(
            input_[op.a], input_[op.b])
        return output

    return opcode


def make_ri(operator_):
    def opcode(op, input_):
        output = input_[:]
        output[op.c] = operator_(input_[op.a], op.b)
        return output

    return opcode


def make_ir(operator_):
    def opcode(op, input_):
        output = input_[:]
        output[op.c] = operator_(op.a, input_[op.b])
        return output

    return opcode


addr = make_rr(operator.add)
addi = make_ri(operator.add)

mulr = make_rr(operator.mul)
muli = make_ri(operator.mul)

banr = make_rr(operator.and_)
bani = make_ri(operator.and_)

borr = make_rr(operator.or_, )
bori = make_ri(operator.or_, )


def setr(op, input_):
    output = input_[:]
    output[op.c] = input_[op.a]
    return output


def seti(op, input_):
    output = input_[:]
    output[op.c] = op.a
    return output


gtir = make_ir(lambda arg1, arg2: 1 if arg1 > arg2 else 0)
gtri = make_ri(lambda arg1, arg2: 1 if arg1 > arg2 else 0)
gtrr = make_rr(lambda arg1, arg2: 1 if arg1 > arg2 else 0)

eqir = make_ir(lambda arg1, arg2: 1 if arg1 == arg2 else 0)
eqri = make_ri(lambda arg1, arg2: 1 if arg1 == arg2 else 0)
eqrr = make_rr(lambda arg1, arg2: 1 if arg1 == arg2 else 0)

OPS = {'addr': addr, 'addi': addi,
       'mulr': mulr, 'muli': muli,
       'banr': banr, 'bani': bani,
       'borr': borr, 'bori': bori,
       'setr': setr, 'seti': seti,
       'gtir': gtir, 'gtri': gtri, 'gtrr': gtrr,
       'eqir': eqir, 'eqri': eqri, 'eqrr': eqrr}


class Machine:

    def __init__(self):
        self.register = [0] * 6
        self.ipreg = 0
        self.program = []

    def load(self, fname):
        with open(fname, 'r') as program:
            line = program.readline()
            self.ipreg = int(line[4:])
            self.program = [parse(line) for line in program]

    def run(self, register=None, do_trace=None):
        if register:
            self.register = register

        trace = []

        while True:
            ip = self.register[self.ipreg]

            if ip >= len(self.program):
                break

            before = self.register[:]
            instr = self.program[ip]

            self.register = OPS[instr.opname](instr, self.register)

            if do_trace:
                trace.append('ip=%d %s %s %d %d %d %s' %
                             (ip, before, instr.opname, instr.a, instr.b, instr.c, self.register))

            self.register[self.ipreg] += 1
        return trace


def show(instr):
    return "%s %d %d %d" % (instr.opname, instr.a, instr.b, instr.c)


def parse(line):
    opname = line[:4]
    a, b, c = map(int, line[4:].split())
    return Op(opname, a, b, c)


def part1(fname):
    machine = Machine()
    machine.load(fname)
    machine.run()
    return machine.register[0]


def part2(fname):
    machine = Machine()
    machine.load(fname)
    machine.run([1, 0, 0, 0, 0, 0])
    return machine.register[0]


def test_parse():
    assert Op(opname='seti', a=5, b=0, c=1) == parse('seti 5 0 1')


def test_run():
    expected = ['ip=0 [0, 0, 0, 0, 0, 0] seti 5 0 1 [0, 5, 0, 0, 0, 0]',
                'ip=1 [1, 5, 0, 0, 0, 0] seti 6 0 2 [1, 5, 6, 0, 0, 0]',
                'ip=2 [2, 5, 6, 0, 0, 0] addi 0 1 0 [3, 5, 6, 0, 0, 0]',
                'ip=4 [4, 5, 6, 0, 0, 0] setr 1 0 0 [5, 5, 6, 0, 0, 0]',
                'ip=6 [6, 5, 6, 0, 0, 0] seti 9 0 5 [6, 5, 6, 0, 0, 9]']
    machine = Machine()
    machine.load('test_input.txt')
    trace = machine.run(do_trace=True)

    assert expected == trace


if __name__ == '__main__':
    print("Part1:", part1('input.txt'))
    # print("Part2:", part2('input.txt'))
