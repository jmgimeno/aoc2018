#include <iostream>
#include <vector>
#include <string>

using namespace std;

struct Scoreboard {
    vector<int> recipes;
    int elf0;
    int elf1;

    Scoreboard(int recipe0, int recipe1) {
        recipes.push_back(recipe0);
        recipes.push_back(recipe1);
        elf0 = 0;
        elf1 = 1;
    }

    int len() {
        return recipes.size();
    }

    void step(int num=1) {
        for (int i = 0; i < num; i++) {
            int recipe0 = recipes[elf0];
            int recipe1 = recipes[elf1];
            int sum_recipes = recipe0 + recipe1;
            if (sum_recipes > 9) 
                recipes.push_back(sum_recipes / 10);
            recipes.push_back(sum_recipes % 10);
            elf0 = (elf0 + recipe0 + 1) % recipes.size();
            elf1 = (elf1 + recipe1 + 1) % recipes.size();
        }
    }

    string slice(int begin, int end) {
        string s;
        for (vector<int>::iterator it = recipes.begin() + begin;
             it < recipes.begin() + end;
             it++) {
                 s.push_back(*it + '0');
             }
        return s;
    }
};

string part1(int number) {
    Scoreboard scoreboard(3, 7);
    while (scoreboard.len() < number + 12) {
        scoreboard.step();
    }
    return scoreboard.slice(number, number+10);
}

void print(vector<int> v) {
    for (vector<int>::const_iterator it = v.begin(); it != v.end(); it++) {
        cout << *it << " ";
    }
    cout << endl;
}

bool found(Scoreboard scoreboard, vector<int> vpattern) {
    int l = scoreboard.len();
    bool before_last = scoreboard.recipes[l-6] == vpattern[0]
                        && scoreboard.recipes[l-5] == vpattern[1]
                        && scoreboard.recipes[l-4] == vpattern[2]
                        && scoreboard.recipes[l-3] == vpattern[3]
                        && scoreboard.recipes[l-2] == vpattern[4];
    if (before_last) return true;
    return scoreboard.recipes[l-5] == vpattern[0]
            && scoreboard.recipes[l-4] == vpattern[1]
            && scoreboard.recipes[l-3] == vpattern[2]
            && scoreboard.recipes[l-2] == vpattern[3]
            && scoreboard.recipes[l-1] == vpattern[4];
}

vector<int> translate(string pattern) {
    vector<int> vpattern;
    for (int i = 0; i < pattern.size(); i++) {
        vpattern.push_back(pattern[i] - '0');
    }
    return vpattern;
}

int part2(string pattern) {
    Scoreboard scoreboard(3, 7);
    vector<int> vpattern = translate(pattern);
    while (scoreboard.len() < 6 || !found(scoreboard, vpattern)) {
        scoreboard.step();
    }
    return scoreboard.len() - 5;
}

void test_part1() {
    assert("0124515891" == part1(5));
    assert("5158916779" == part1(9));
    assert("9251071085" == part1(18));
    assert("5941429882" == part1(2018));
}

void test_part2() {
    assert(5 == part2("01245"));
    assert(9 == part2("51589"));
    assert(18 == part2("92510"));
    assert(2018 == part2("59414"));
}

int main() {
    //test_part1();
    //test_part2();
    cout << "Part1: " << part1(30121) << endl;
    cout << "Part2: " << part2("030121") << endl;
}