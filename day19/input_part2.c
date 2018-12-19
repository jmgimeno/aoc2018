
#include <stdio.h>

long regs[] = {1, 0, 0, 0, 0, 0};

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
    switch(regs[2]) {
      case 0: addi(2, 16, 2); break;
      case 1: seti(1, 1, 3); break;
      case 2: seti(1, 7, 5); break;
      case 3: mulr(3, 5, 4); break;
      case 4: eqrr(4, 1, 4); break;
      case 5: addr(4, 2, 2); break;
      case 6: addi(2, 1, 2); break;
      case 7: addr(3, 0, 0); break;
      case 8: addi(5, 1, 5); break;
      case 9: gtrr(5, 1, 4); break;
      case 10: addr(2, 4, 2); break;
      case 11: seti(2, 3, 2); break;
      case 12: addi(3, 1, 3); break;
      case 13: gtrr(3, 1, 4); break;
      case 14: addr(4, 2, 2); break;
      case 15: seti(1, 9, 2); break;
      case 16: mulr(2, 2, 2); break;
      case 17: addi(1, 2, 1); break;
      case 18: mulr(1, 1, 1); break;
      case 19: mulr(2, 1, 1); break;
      case 20: muli(1, 11, 1); break;
      case 21: addi(4, 3, 4); break;
      case 22: mulr(4, 2, 4); break;
      case 23: addi(4, 13, 4); break;
      case 24: addr(1, 4, 1); break;
      case 25: addr(2, 0, 2); break;
      case 26: seti(0, 1, 2); break;
      case 27: setr(2, 0, 4); break;
      case 28: mulr(4, 2, 4); break;
      case 29: addr(2, 4, 4); break;
      case 30: mulr(2, 4, 4); break;
      case 31: muli(4, 14, 4); break;
      case 32: mulr(4, 2, 4); break;
      case 33: addr(1, 4, 1); break;
      case 34: seti(0, 4, 0); break;
      case 35: seti(0, 5, 2); break;
      default: printf("Execution: %ld\n", regs[0]); return 0;
    }
    regs[2] += 1;
  }
}
