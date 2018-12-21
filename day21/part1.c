
#include <stdio.h>
#include <limits.h>

int regs[] = {0, 0, 0, 0, 0, 0};

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
  int counter = 0;
  while (1) {
    switch(regs[2]) {
      case 0: seti(123, 0, 5); break;
      case 1: bani(5, 456, 5); break;
      case 2: eqri(5, 72, 5); break;
      case 3: addr(5, 2, 2); break;
      case 4: seti(0, 0, 2); break;
      case 5: seti(0, 4, 5); break;
      case 6: bori(5, 65536, 1); break;
      case 7: seti(10678677, 3, 5); break;
      case 8: bani(1, 255, 4); break;
      case 9: addr(5, 4, 5); break;
      case 10: bani(5, 16777215, 5); break;
      case 11: muli(5, 65899, 5); break;
      case 12: bani(5, 16777215, 5); break;
      case 13: gtir(256, 1, 4); break;
      case 14: addr(4, 2, 2); break;
      case 15: addi(2, 1, 2); break;
      case 16: seti(27, 5, 2); break;
      case 17: seti(0, 6, 4); break;
      case 18: addi(4, 1, 3); break;
      case 19: muli(3, 256, 3); break;
      case 20: gtrr(3, 1, 3); break;
      case 21: addr(3, 2, 2); break;
      case 22: addi(2, 1, 2); break;
      case 23: seti(25, 4, 2); break;
      case 24: addi(4, 1, 4); break;
      case 25: seti(17, 6, 2); break;
      case 26: setr(4, 6, 1); break;
      case 27: seti(7, 5, 2); break;
      case 28: eqrr(5, 0, 4); printf("Part1: %d\n", regs[5]); return 0;
      case 29: addr(4, 2, 2); break;
      case 30: seti(5, 4, 2); break;
      default: printf("Finished %d: %d\n", regs[0], counter); return 0;
    }
    regs[2] += 1;
    counter += 1;
  }
}
