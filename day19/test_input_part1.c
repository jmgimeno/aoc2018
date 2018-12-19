
#include <stdio.h>

long regs[] = {0, 0, 0, 0, 0, 0};

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
    switch(regs[0]) {
      case 0: seti(5, 0, 1); break;
      case 1: seti(6, 0, 2); break;
      case 2: addi(0, 1, 0); break;
      case 3: addr(1, 2, 3); break;
      case 4: setr(1, 0, 0); break;
      case 5: seti(8, 0, 4); break;
      case 6: seti(9, 0, 5); break;
      default: printf("Execution: %ld\n", regs[0]); return 0;
    }
    regs[0] += 1;
  }
}
