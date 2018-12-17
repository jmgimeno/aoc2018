#include <iostream>
#include <vector>
#include <string>

using namespace std;

class Scoreboards {
    vector<int> recipes;
    int elf0;
    int elf1;
    int recipe0;
    int recipe1;
    int next_recipe;
    
    public: 

    Scoreboards(int recipe0, int recipe1) {
        recipes.push_back(recipe0);
        recipes.push_back(recipe1);
        elf0 = 0;
        elf1 = 1;
        next_recipe = -1;
    }

    const vector<int>& next() {
        if (next_recipe == -1) {
            recipe0 = recipes[elf0];
            recipe1 = recipes[elf1];
            int sum_recipes = recipe0 + recipe1;
            if (sum_recipes > 9) {
                recipes.push_back(sum_recipes / 10);
                next_recipe = sum_recipes % 10;
            } else {
                recipes.push_back(sum_recipes);
                elf0 = (elf0 + recipe0 + 1) % recipes.size();
                elf1 = (elf1 + recipe1 + 1) % recipes.size();
            }
        } else {
            recipes.push_back(next_recipe);
            next_recipe = -1;
            elf0 = (elf0 + recipe0 + 1) % recipes.size();
            elf1 = (elf1 + recipe1 + 1) % recipes.size();
        }
        return recipes;
    }
};

string stringuify(const vector<int>& v, int begin, int end) {
    string s;
    for (int i = begin; i < end; i++) {
        s.push_back(v[i] + '0');
    }
    return s;
}

void print(vector<int>& v) {
    for (int i = 0; i < v.size(); i++) {
        cout << v[i] << " ";
    }
    cout << endl;
}

string part1(int number) {
    Scoreboards scoreboards(3, 7);
    const vector<int>& scoreboard = scoreboards.next();
    do {
        scoreboards.next();
    } while (scoreboard.size() < number + 12);
    return stringuify(scoreboard, number, number+10);
}

vector<int> vectorify(string s) {
    vector<int> v;
    for (int i = 0; i < s.size(); i++) {
        v.push_back(s[i] - '0');
    }
    return v;
}

bool has_suffix(const vector<int>& scoreboard, const vector<int>& suffix) {
    if (scoreboard.size() < suffix.size()) {
        return false;
    }
    for (int i = 0; i < suffix.size(); i++) {
        if (scoreboard[scoreboard.size()-suffix.size()+i] != suffix[i]) {
            return false;
        }
    }
    return true;
}

int part2(string pattern) {
    const vector<int> vpattern = vectorify(pattern);
    Scoreboards scoreboards(3, 7);
    const vector<int>& scoreboard = scoreboards.next();
    do {
        scoreboards.next();
    } while (!has_suffix(scoreboard, vpattern));
    return scoreboard.size() - vpattern.size();
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