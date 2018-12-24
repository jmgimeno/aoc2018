import re

line_regexp = re.compile(
    (r'^(?P<quantity>\d+) units each with (?P<hit_points>\d+) hit points'
     r' (?P<weaknesses_or_immunities>\(.+\))?\s?with an attack that does'
     r' (?P<attack_damage>\d+) (?P<attack_type>\w+) damage at initiative'
     r' (?P<initiative>\d+)$'))


class Group:

    def __init__(self, quantity, hit_points, weaknesses, immunities,
                 attack_damage, attack_type, initiative, kind=None):
        self.quantity = quantity
        self.hit_points = hit_points
        self.weaknesses = weaknesses
        self.immunities = immunities
        self.attack_damage = attack_damage
        self.attack_type = attack_type
        self.initiative = initiative
        self.kind = kind

    def __eq__(self, other):
        if not isinstance(other, Group):
            return False
        return (self.quantity == other.quantity
                and self.hit_points == other.hit_points
                and self.weaknesses == other.weaknesses
                and self.immunities == other.immunities
                and self.attack_damage == other.attack_damage
                and self.attack_type == other.attack_type
                and self.initiative == other.initiative
                and self.kind == other.kind)

    @staticmethod
    def from_line(line, kind=None):
        match_groups = line_regexp.match(line).groupdict()
        weaknesses, immunities = parse_weaknesses_or_immunities(match_groups['weaknesses_or_immunities'])
        return Group(quantity=int(match_groups['quantity']),
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
    group = Group(quantity=17,
                  hit_points=5390,
                  weaknesses=['radiation', 'bludgeoning'],
                  immunities=[],
                  attack_damage=4507,
                  attack_type='fire',
                  initiative=2)

    assert Group.from_line(line) == group


class Simulation:

    def __init__(self, immune_system, infection):
        self.immune_system = immune_system
        self.infection = infection

    def __eq__(self, other):
        if not isinstance(other, Simulation):
            return False
        return (self.immune_system == other.immune_system
                and self.infection == other.infection)

    @staticmethod
    def load_from_file(fname):
        with open(fname, 'r') as file:
            immune_system = []
            file.readline()  # Immune System
            while True:
                line = file.readline().strip()
                if len(line) == 0:
                    break
                immune_system.append(Group.from_line(line, kind='ImmuneSystem'))
            infection = []
            file.readline()  # Infection
            while True:
                line = file.readline().strip()
                if len(line) == 0:
                    break
                infection.append(Group.from_line(line, kind="Infection"))
            return Simulation(immune_system, infection)

    def fight(self):
        # target selection
        immune_system_targets = Simulation.get_targets(self.immune_system, self.infection)
        infection_targets = Simulation.get_targets(self.infection, self.immune_system)

        # attacking
        attacking_order = sorted(self.immune_system + self.infection,
                                 key=lambda group: -group.initiative)
        for attacker in attacking_order:
            if attacker.quantiy <= 0:
                continue
            if attacker.kind == 'ImmuneSystem':
                pass

    def run(self):
        while len(self.immune_system) > 0 and len(self.infection) > 0:
            self.fight()

    @staticmethod
    def get_targets(attackers, defenders):
        targets = {}
        remaining_defenders = set(range(defenders))
        attacker_order = sorted(
            range(attackers),
            key=lambda idx: (-attackers[idx].effective_power(),
                             -attackers[idx].initiative))
        for idx_attacker in attacker_order:
            target = max(remaining_defenders,
                         key=lambda idx_defender: (get_damage(attackers[idx_attacker],
                                                              defenders[idx_defender]),
                                                   defenders[idx_defender].effective_power(),
                                                   defenders[idx_defender].initiative))
            if get_damage(attackers[idx_attacker], defenders[target]) > 0:
                targets[idx_attacker] = target
                defenders.remove(target)
        return targets


def get_damage(attacker, defender):
    damage = attacker.effective_power()
    if attacker.attack_type in defender.immunities:
        return 0
    elif attacker.attack_type in defender.weaknesses:
        return damage * 2
    else:
        return damage


def test_simulation_load_from_file():
    simulalion = Simulation(
        immune_system=[
            Group(quantity=17,
                  hit_points=5390,
                  weaknesses=['radiation', 'bludgeoning'],
                  immunities=[],
                  attack_damage=4507,
                  attack_type='fire',
                  initiative=2,
                  kind='ImmuneSystem'),
            Group(quantity=989,
                  hit_points=1274,
                  weaknesses=['bludgeoning', 'slashing'],
                  immunities=['fire'],
                  attack_damage=25,
                  attack_type='slashing',
                  initiative=3,
                  kind='ImmuneSystem')
        ],
        infection=[
            Group(quantity=801,
                  hit_points=4706,
                  weaknesses=['radiation'],
                  immunities=[],
                  attack_damage=116,
                  attack_type='bludgeoning',
                  initiative=1,
                  kind='Infection'),
            Group(quantity=4485,
                  hit_points=2961,
                  weaknesses=['fire', 'cold'],
                  immunities=['radiation'],
                  attack_damage=12,
                  attack_type='slashing',
                  initiative=4,
                  kind='Infection')
        ]
    )
    assert Simulation.load_from_file('test_input.txt') == simulalion

    def get_infection_targets(self):
        pass
