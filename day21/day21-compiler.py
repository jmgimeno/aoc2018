import os
import string

TEMPLATE = string.Template("""
#include <stdio.h>

int regs[] = $registers;

void addr(int a, int b, int c) {
  regs[c] = regs[a] + regs[b];
}

void addi(int a, int b, int c) {
  regs[c] = regs[a] + b;
}

void mulr(int a, int b, int c) {
  regs[c] = regs[a] * regs[b];
}

void muli(int a, int b, int c) {
  regs[c] = regs[a] * b;
}

void banr(int a, int b, int c) {
  regs[c] = regs[a] & regs[b];
}

void bani(int a, int b, int c) {
  regs[c] = regs[a] & b;
}

void borr(int a, int b, int c) {
  regs[c] = regs[a] | regs[b];
}

void bori(int a, int b, int c) {
  regs[c] = regs[a] | b;
}

void setr(int a, int b, int c) {
  regs[c] = regs[a];
}

void seti(int a, int b, int c) {
  regs[c] = a;
}

void gtir(int a, int b, int c) {
  regs[c] = (a > regs[b]) ? 1 : 0;
}

void gtri(int a, int b, int c) {
  regs[c] = (regs[a] > b) ? 1 : 0;
}

void gtrr(int a, int b, int c) {
  regs[c] = (regs[a] > regs[b]) ? 1 : 0;
}

void eqir(int a, int b, int c) {
  regs[c] = (a == regs[b]) ? 1 : 0;
}

void eqri(int a, int b, int c) {
  regs[c] = (regs[a] == b) ? 1 : 0;
}

void eqrr(int a, int b, int c) {
  regs[c] = (regs[a] == regs[b]) ? 1 : 0;
}

int main() {
  while (1) {
    switch(regs[$ipreg]) {
$cases
      default: printf("Execution: %d\\n", regs[0]); return 0;
    }
    regs[$ipreg] += 1;
  }
}
""")


def compile_line(line):
    opname = line[:4]
    a, b, c = line[4:].split()
    return '%s(%s, %s, %s);' % (opname, a, b, c)


def compile_lines(lines):
    cases = []
    for lineno, line in enumerate(lines):
        cases.append('      case %d: %s break;' % (lineno, compile_line(line)))
    return '\n'.join(cases)


def compile_file(fname, registers):
    with open(fname, 'r') as program:
        registers = str(registers).replace('[', '{').replace(']', '}')
        ipreg = program.readline().strip()[4:]
        cases = compile_lines(line.strip() for line in program)
        return TEMPLATE.substitute(ipreg=ipreg, cases=cases, registers=registers)


def part1(fname):
    name, _ = os.path.splitext(fname)
    with open(name + '_part1.c', 'w') as compiled:
        program = compile_file(fname, [0, 0, 0, 0, 0, 0])
        compiled.write(program)




if __name__ == "__main__":
    part1('input.txt')
