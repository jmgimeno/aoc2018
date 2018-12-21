#include <iostream>
#include <set>

using namespace std;

int main() {
  set<int> seen;
  int last_r5 = 0;
  int r0, r1, r3, r4, r5;

  l6: 
  r1 = r5 | 65536;
  r5 = 10678677;
  
  l8:
  r4 = r1 & 255;
  r5 += r4;
  r5 &= 16777215;
  r5 *= 65899;
  r5 &= 16777215;
  if (256 > r1) goto l28;
  r4 = 0;
  
  l18:
  r3 = r4 + 1;
  r3 *= 256;
  if (r3 > r1) goto l26;
  r4 += 1;
  goto l18;
  
  l26:
  r1 = r4;
  goto l8;

  l28:
  if (last_r5 == 0) {
    cout << "Part1: " << r5 << endl;
  }
  if (seen.find(r5) == seen.end()) {
    seen.insert(r5);
    last_r5 = r5;
  } else {
    cout << "Part2: " << last_r5 << endl;
    return 0;
  }
  goto l6;
}