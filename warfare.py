import stats_listing
import sys

WOUNDMAPPING = {0: 0.5, 1: 0.667, 2: 0.83, 3: 0.83, 4: 0.83, 5: 0.83, 6: 0.83,
                7: 0.83, 8: 0.83, 9: 0.83, -1: 0.33, -2: 0.167, -3: 0.167,
                -4: 0.167, -5: 0.167, -6: 0.167, -7: 0.167, -8: 0.167,
                -9: 0.167, }

SAVERATIO = {6: 0.167, 5: 0.33, 4: 0.5, 3: 0.667, 2: 0.83}


def check_init(u1_init, u2_init):
    """check who goes first"""

    if u1_init > u2_init:
        return {'first': 'unit_one', 'second': 'unit_two'}
    if u1_init == u2_init:
        return {'first': 'same_time'}
    else:
        return {'first': 'unit_two', 'second': 'unit_one'}


def generate_attacks(model_att_value, number_of_models, charging=False):
    """this will generate the number of attacks"""
    attacks = int(model_att_value) * int(number_of_models)
    if charging:
        attacks = attacks + number_of_models
    #fixme this is returning a sequence and the wrong number too
    return attacks


def resolve_deaths(wounds_value, number_of_models, amount_of_unsaved_wounds):
    """figure out the amount of casualities suffered"""
    units_wounds = wounds_value * number_of_models
    print units_wounds, amount_of_unsaved_wounds
    new_number_of_models = int(units_wounds) - amount_of_unsaved_wounds
    return new_number_of_models


def melee_to_hit(attacker_ws, defender_ws, number_of_attacks):
    """checks the percentages of hits"""
    hit_rate = float(0.5)
    if attacker_ws > defender_ws:
        hit_rate = float(0.667)
    return int(number_of_attacks) * hit_rate


def to_wound(attacker_str, defender_tough, number_of_hits):
    """this will check if the hit is a wound
        strength - toughness and find ratio in dict
    """
    wounds = attacker_str - defender_tough
    if defender_tough == attacker_str *2:
        return 0
    return number_of_hits * WOUNDMAPPING[wounds]


def armour_save(attacker_ap, defender_save, number_of_wounds, defender_inv=None):
    """this will determine if a wound is a kill"""
    ratio = SAVERATIO[defender_save]
    if attacker_ap <= defender_save and not defender_inv:
        ratio = 1
    elif defender_inv and attacker_ap <= defender_save:
        ratio = SAVERATIO[defender_inv]
    unsaved_wounds = number_of_wounds * ratio
    return unsaved_wounds


def shooting(attacker, defender, shots):
    pass


def combat_result(defender, attacker, attacks):
    enemy_invun = None
    wounds = melee_to_hit(attacker['ws'], defender['ws'], attacks)
    saves = to_wound(attacker['strength'], defender['toughness'], wounds)
    try:
        if defender['invun_save']:
                    enemy_invun = defender['invun_save']
    except KeyError:
        enemy_invun = None
    wounds_caused = armour_save(attacker['ap'], defender['save'], saves,
                                enemy_invun)
    return wounds_caused


def combat(unit_one, unit_one_size,  unit_two, unit_two_size, who_charged):
    """this will work out the sequence of combat based on init"""

    #expand the units
    try:
        unit_one = stats_listing.assorted[unit_one.lower()]
    except KeyError:
        return 'error with unit 1'
    try:
        unit_two = stats_listing.assorted[unit_two.lower()]
    except KeyError:
        return 'error with unit 2'

    charging = False
    #figure out who attacks first to remove valid models from unit_two
    init_order = check_init(unit_one['initiative'], unit_two['initiative'])


    if init_order['first'] == 'unit_one':
        if who_charged == unit_one:
            #fixme unit_one is a dict, and who_charged is a unit name
            charging = True
        friendly_attacks = generate_attacks(unit_one['attacks'], unit_one_size,
                                            charging)
        wounds = combat_result(unit_two, unit_one, friendly_attacks)
        new_size_of_unit_two = resolve_deaths(unit_two['wounds'], unit_two_size,
                                              wounds)
        # print new_size_of_unit_two
        if new_size_of_unit_two < 1:
            print "wiped out"
        first_kill_tally = unit_two_size - new_size_of_unit_two
        if who_charged == unit_two:
                charging = True
        enemy_attacks = generate_attacks(unit_two['attacks'],
                                         new_size_of_unit_two, charging)
        wounds_returned = combat_result(unit_two, unit_one, enemy_attacks)
        new_size_of_unit_one = resolve_deaths(unit_one['wounds'], unit_one,
                                              wounds_returned)
        second_kill_tally = unit_one_size - new_size_of_unit_one
        print(
        '%s %s fought %s %s. After %s attacked %s times and scored %s wounds '
        'the size of %s was reduced to %s. Then %s attacked back and scored '
        '%s hits and %s wounds reducing %s to %s').format(
            unit_one_size, unit_one, unit_two_size, unit_two, unit_one,
            friendly_attacks, wounds, unit_two, new_size_of_unit_two, unit_two,
            enemy_attacks, wounds_returned, unit_one, new_size_of_unit_one)
        print('%s scored %s kills and'
              ' %s scored %s kills').format(unit_one,
                                            first_kill_tally,
                                            unit_two,
                                            second_kill_tally)

    elif init_order['first'] == 'unit_two':
        if who_charged == unit_two:
            charging = True
        friendly_attacks = generate_attacks(unit_two['attacks'], unit_two_size,
                                            charging)
        wounds = combat_result(unit_one, unit_two, friendly_attacks)

        new_size_of_unit_one = resolve_deaths(unit_one['wounds'], unit_one_size,
                                              wounds)
        if new_size_of_unit_one < 1:
            return "wiped out"

        if who_charged == unit_one:
                charging = True
        enemy_attacks = generate_attacks(unit_one['attacks'],
                                         new_size_of_unit_one, charging)
        wounds_returned = combat_result(unit_one, unit_two, enemy_attacks)
        new_size_of_unit_two = resolve_deaths(unit_two['wounds'], unit_two,
                                              wounds_returned)

if __name__ == '__main__':
    #using sys.argv - which outputs a list but you need to ignore option "0"
    #as this is the filename
    #argparse or optparse
    arg_1 = 'scorpion'
    arg_2 = 10
    arg_3 = 'assualtmarine'
    arg_4 = 10
    arg_5 = 'scorpion'
    combat(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
