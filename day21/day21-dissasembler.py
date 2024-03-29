import os

OPS = {'addi': 'r[{c}] = r[{a}] + {b}',
       'addr': 'r[{c}] = r[{a}] + r[{b}]',
       'muli': 'r[{c}] = r[{a}] * 0x{b:08x}',
       'mulr': 'r[{c}] = r[{a}] * r[{b}]',
       'seti': 'r[{c}] = 0x{a:08x}',
       'setr': 'r[{c}] = r[{a}]',
       'eqrr': 'r[{c}] = 1 if r[{a}] == r[{b}] else 0',
       'eqri': 'r[{c}] = 1 if r[{a}] == 0x{b:08x} else 0',
       'gtrr': 'r[{c}] = 1 if r[{a}] > r[{b}] else 0',
       'gtir': 'r[{c}] = 1 if 0x{a:08x} > r[{b}] else 0',
       'bani': 'r[{c}] = r[{a}] & 0x{b:08x}',
       'bori': 'r[{c}] = r[{a}] | 0x{b:08x}'
       }


def disassemble_line(line, lineno, ipreg):
    opname = line[:4]
    a, b, c = map(int, line[4:].split())
    if opname == 'addi' and c == ipreg and a == ipreg:
        return 'jump #%d' % (b+lineno+1,)
    elif opname == 'addr' and c == ipreg and a == ipreg:
        return 'jump r[%d] + %d' % (b, lineno+1)
    elif opname == 'addr' and c == ipreg and b == ipreg:
        return 'jump r[%d] + %d' % (a, lineno+1)
    elif opname == 'seti' and c == ipreg:
        return 'jump #%d' % (a+1,)
    elif opname == 'mulr' and a == ipreg and b == ipreg and c == ipreg:
        return 'jump #%d' %(lineno * lineno + 1,)
    elif opname == 'addr' and b == ipreg:
        return 'r[%d] = r[%d] + %d' %(c, a, lineno)
    elif opname == 'addr' and a == ipreg:
        return 'r[%d] = r[%d] + %d' % (c, b, lineno)
    elif opname == 'mulr' and b == ipreg:
        return 'r[%d] = r[%d] * %d' %(c, a, lineno)
    elif opname == 'mulr' and a == ipreg:
        return 'r[%d] = r[%d] * %d' % (c, b, lineno)
    elif opname == 'setr' and a == ipreg:
        return 'r[%d] = %d' % (c, lineno)
    else:
        return OPS[opname].format(a=a, b=b, c=c)


def disassemble_lines(lines, ipreg):
    cases = []
    for lineno, line in enumerate(lines):
        cases.append("%2d# %s" % (lineno, disassemble_line(line, lineno, ipreg)))
    return '\n'.join(cases)


def disassemble_file(fname, registers):
    with open(fname, 'r') as program:
        ipreg = int(program.readline()[4:])
        registers = 'r = ' + str(registers) + '\n'
        instructions = disassemble_lines((line.strip() for line in program), ipreg)
        return registers, instructions


def part1(fname):
    name, _ = os.path.splitext(fname)
    with open(name + '_disassembled.txt', 'w') as compiled:
        registers, instructions = disassemble_file(fname, [1, 0, 0, 0, 0, 0])
        compiled.write(registers)
        compiled.write(instructions)


if __name__ == "__main__":
    part1('../data/day21-input.txt')
