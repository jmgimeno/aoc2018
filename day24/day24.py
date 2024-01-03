import copy
import re

line_regexp = re.compile(
    (r'^(?P<quantity>\d+) units each with (?P<hit_points>\d+) hit points'
     r' (?P<weaknesses_or_immunities>\(.+\))?\s?with an attack that does'
     r' (?P<attack_damage>\d+) (?P<attack_type>\w+) damage at initiative'
     r' (?P<initiative>\d+)$'))


class Group:
    counter = 0

    def __init__(self, id, quantity, hit_points, weaknesses, immunities,
                 attack_damage, attack_type, initiative, kind=None):
        self.id = id
        self.quantity = quantity
        self.hit_points = hit_points
        self.weaknesses = weaknesses
        self.immunities = immunities
        self.attack_damage = attack_damage
        self.attack_type = attack_type
        self.initiative = initiative
        self.kind = kind
        Group.counter += 1

    def __eq__(self, other):
        if not isinstance(other, Group):
            return False
        return (self.id == other.id
                and self.quantity == other.quantity
                and self.hit_points == other.hit_points
                and self.weaknesses == other.weaknesses
                and self.immunities == other.immunities
                and self.attack_damage == other.attack_damage
                and self.attack_type == other.attack_type
                and self.initiative == other.initiative
                and self.kind == other.kind)

    def __repr__(self):
        return '%d: %s(%d - %d)' % (self.id, self.kind, self.quantity, self.attack_damage)

    @staticmethod
    def from_line(id, line, kind=None):
        match_groups = line_regexp.match(line).groupdict()
        w_o_p = match_groups['weaknesses_or_immunities']
        if w_o_p is not None:
            weaknesses, immunities = parse_weaknesses_or_immunities(w_o_p)
        else:
            weaknesses = []
            immunities = []
        return Group(id=id,
                     quantity=int(match_groups['quantity']),
                     hit_points=int(match_groups['hit_points']),
                     weaknesses=weaknesses,
                     immunities=immunities,
                     attack_damage=int(match_groups['attack_damage']),
                     attack_type=match_groups['attack_type'],
                     initiative=int(match_groups['initiative']),
                     kind=kind)

    def effective_power(self):
        return self.quantity * self.attack_damage


def parse_weaknesses_or_immunities(w_or_i):
    weakness_start = w_or_i.find('weak to ')
    if weakness_start == -1:
        weaknesses = []
    else:
        weakness_start += 8
        weakness_end = min(w_or_i.find(';', weakness_start), w_or_i.find(')', weakness_start))
        weaknesses = [w.strip() for w in w_or_i[weakness_start:weakness_end].split(',')]
    immunity_start = w_or_i.find('immune to ')
    if immunity_start == -1:
        immunities = []
    else:
        immunity_start += 10
        immunity_end = min(w_or_i.find(';', immunity_start), w_or_i.find(')', immunity_start))
        immunities = [w.strip() for w in w_or_i[immunity_start:immunity_end].split(',')]
    return weaknesses, immunities


def test_parse_weaknesses_or_immunities():
    assert parse_weaknesses_or_immunities('(weak to radiation, bludgeoning)') == \
           (['radiation', 'bludgeoning'], [])
    assert parse_weaknesses_or_immunities('(immune to fire; weak to bludgeoning, slashing)') == \
           (['bludgeoning', 'slashing'], ['fire'])
    assert parse_weaknesses_or_immunities('weak to bludgeoning; immune to cold)') == \
           (['bludgeoning'], ['cold'])


def test_group_fromline():
    line = ('17 units each with 5390 hit points (weak to radiation, bludgeoning)'
            'with an attack that does 4507 fire damage at initiative 2')
    group = Group(id=0,
                  quantity=17,
                  hit_points=5390,
                  weaknesses=['radiation', 'bludgeoning'],
                  immunities=[],
                  attack_damage=4507,
                  attack_type='fire',
                  initiative=2)

    assert Group.from_line(0, line) == group


class Stalemate(Exception):
    pass


class Simulation:

    def __init__(self, groups):
        self.groups = groups

    def __eq__(self, other):
        if not isinstance(other, Simulation):
            return False
        return self.groups == other.groups

    @staticmethod
    def load_from_file(fname):
        with open(fname, 'r') as file:
            groups = []
            file.readline()  # Immune System
            lineno = 0
            while True:
                line = file.readline().strip()
                if len(line) == 0:
                    break
                groups.append(Group.from_line(lineno, line, kind='ImmuneSystem'))
                lineno += 1
            file.readline()  # Infection
            while True:
                line = file.readline().strip()
                if len(line) == 0:
                    break
                groups.append(Group.from_line(lineno, line, kind="Infection"))
                lineno += 1
            return Simulation(groups)

    def fight(self, immune_system, infection):

        # target selection
        immune_system_targets = self.get_targets(immune_system, infection)
        infection_targets = self.get_targets(infection, immune_system)

        # attacking
        attacking_order = sorted(self.groups,
                                 key=lambda group: -group.initiative)

        changed = False
        for attacker in attacking_order:
            if attacker.quantity <= 0:
                continue
            if attacker.kind == 'ImmuneSystem':
                defender_id = immune_system_targets.get(attacker.id)
            else:
                defender_id = infection_targets.get(attacker.id)
            if defender_id is not None:
                defender = self.groups[defender_id]
                before = defender.quantity
                Simulation.attack(attacker, defender)
                if defender.quantity != before:
                    changed = True

        return changed

    @staticmethod
    def attack(attacker, defender):
        damage = get_damage(attacker, defender)
        defender.quantity -= damage // defender.hit_points

    def run(self):
        while True:
            immune_system = [group for group in self.groups if group.kind == 'ImmuneSystem' and group.quantity > 0]
            infection = [group for group in self.groups if group.kind == 'Infection' and group.quantity > 0]
            if len(immune_system) == 0 or len(infection) == 0:
                break
            change = self.fight(immune_system, infection)
            if not change:
                raise Stalemate()
        return (sum(imm.quantity for imm in immune_system)
                + sum(inf.quantity for inf in infection))

    def get_targets(self, attackers, defenders):
        targets = {}
        remaining_defenders = {defender.id for defender in defenders}
        attacker_order = sorted(
            attackers,
            key=lambda att: (-att.effective_power(), -att.initiative))

        for attacker in attacker_order:
            if len(remaining_defenders) == 0:
                break
            target = max(remaining_defenders,
                         key=lambda idx_defender: (get_damage(attacker,
                                                              self.groups[idx_defender]),
                                                   self.groups[idx_defender].effective_power(),
                                                   self.groups[idx_defender].initiative))

            if get_damage(attacker, self.groups[target]) > 0:
                targets[attacker.id] = target
                remaining_defenders.remove(target)
        return targets

    def boost_immune_system(self, boost):
        for group in self.groups:
            if group.kind == 'ImmuneSystem':
                group.attack_damage += boost


def part2(fname):
    simulation = Simulation.load_from_file(fname)
    boost = 1
    while True:
        print('Current boost', boost)
        current_simulation = copy.deepcopy(simulation)
        current_simulation.boost_immune_system(boost)
        try:
            result = current_simulation.run()
            print(result)
            if (any(group for group in current_simulation.groups if group.kind == 'ImmuneSystem' and group.quantity > 0)
                    and all(group for group in current_simulation.groups if group.kind == 'Infection' and group.quantity <= 0)):
                return boost, result
        except Stalemate:
            pass
        boost += 1


def get_damage(attacker, defender):
    damage = attacker.effective_power()
    if attacker.attack_type in defender.immunities:
        return 0
    elif attacker.attack_type in defender.weaknesses:
        return damage * 2
    else:
        return damage


def part1(fname):
    simulation = Simulation.load_from_file(fname)
    return simulation.run()


def test_simulation_load_from_file():
    simulation = Simulation([
        Group(id=0,
              quantity=17,
              hit_points=5390,
              weaknesses=['radiation', 'bludgeoning'],
              immunities=[],
              attack_damage=4507,
              attack_type='fire',
              initiative=2,
              kind='ImmuneSystem'),
        Group(id=1,
              quantity=989,
              hit_points=1274,
              weaknesses=['bludgeoning', 'slashing'],
              immunities=['fire'],
              attack_damage=25,
              attack_type='slashing',
              initiative=3,
              kind='ImmuneSystem'),
        Group(id=2,
              quantity=801,
              hit_points=4706,
              weaknesses=['radiation'],
              immunities=[],
              attack_damage=116,
              attack_type='bludgeoning',
              initiative=1,
              kind='Infection'),
        Group(id=3,
              quantity=4485,
              hit_points=2961,
              weaknesses=['fire', 'cold'],
              immunities=['radiation'],
              attack_damage=12,
              attack_type='slashing',
              initiative=4,
              kind='Infection')])

    assert Simulation.load_from_file('test_input.txt') == simulation


def test_part1():
    assert part1('test_input.txt') == 5216

def test_part2():
    assert part2('test_input.txt')[1] == 51


if __name__ == '__main__':
    print('Part1: ', part1('../data/day24-input.txt'))
    print('Part2: ', part2('../data/day24-input.txt'))
