"""Checks kidney_swap/pool.py (owner: Generator).

Run:  uv run python simple_plan/checks/check_pool.py
"""

from helpers import (BLOOD_GROUPS, blood_ok, check, fail, finish, get, require, timed)

pool_module = require("pool", owner="Generator")


def t_constants():
    groups = get(pool_module, "BLOOD_GROUPS")
    if sorted(groups) != sorted(BLOOD_GROUPS):
        fail(f"BLOOD_GROUPS should be ['O', 'A', 'B', 'AB'], but it is {groups!r}.")
    mix = get(pool_module, "INDIA_BLOOD_MIX")
    if not isinstance(mix, dict):
        fail("INDIA_BLOOD_MIX should be a dict like {'O': 0.3, 'A': 0.2, ...}.")
    if sorted(mix.keys()) != sorted(BLOOD_GROUPS):
        fail(f"INDIA_BLOOD_MIX must have exactly the keys O, A, B, AB. It has {sorted(mix.keys())}.")
    for group, share in mix.items():
        if not 0 < share < 1:
            fail(f"INDIA_BLOOD_MIX['{group}'] = {share}. Shares are fractions between 0 and 1, not percents.")
    if abs(sum(mix.values()) - 1.0) > 0.01:
        fail(f"The shares in INDIA_BLOOD_MIX add up to {sum(mix.values()):.3f}. They must add up to 1.0.")
    chance = get(pool_module, "TISSUE_PASS_CHANCE")
    if not 0 < chance < 1:
        fail(f"TISSUE_PASS_CHANCE = {chance}. It should be a probability between 0 and 1, like 0.89.")


def t_can_give():
    can_give = get(pool_module, "can_give")
    wrong = []
    for donor in BLOOD_GROUPS:
        for patient in BLOOD_GROUPS:
            answer = can_give(donor, patient)
            if answer is not True and answer is not False:
                fail(f"can_give('{donor}', '{patient}') returned {answer!r}. It must return True or False.")
            if answer != blood_ok(donor, patient):
                wrong.append(f"can_give(donor='{donor}', patient='{patient}') returned {answer}, "
                             f"should be {blood_ok(donor, patient)}")
    if wrong:
        fail("Some blood rules are wrong:\n" + "\n".join(wrong) +
             "\nRule: O gives to everyone; A gives to A and AB; B gives to B and AB; AB gives only to AB."
             "\nCheck the argument order: can_give(donor, patient).")


def t_family():
    Family = get(pool_module, "Family")
    family = Family(7, "A", "B")
    for attribute, expected in (("id", 7), ("patient_blood", "A"), ("donor_blood", "B")):
        if not hasattr(family, attribute):
            fail(f"Family(7, 'A', 'B') has no attribute '{attribute}'. "
                 f"Set self.{attribute} in __init__(self, id, patient_blood, donor_blood).")
        if getattr(family, attribute) != expected:
            fail(f"Family(7, 'A', 'B').{attribute} is {getattr(family, attribute)!r}, should be {expected!r}. "
                 f"Check the order of the __init__ arguments.")


def t_pool_class():
    Family = get(pool_module, "Family")
    Pool = get(pool_module, "Pool")
    families = [Family(1, "A", "B"), Family(2, "B", "A")]
    arrows = {(1, 2), (2, 1)}
    pool = Pool(families, arrows)
    if getattr(pool, "families", None) != families:
        fail("Pool(families, arrows).families should be the list of families you passed in.")
    if getattr(pool, "arrows", None) != arrows:
        fail("Pool(families, arrows).arrows should be the set of arrows you passed in.")


def make(n, seed):
    make_pool = get(pool_module, "make_pool")
    pool = make_pool(n, seed)
    if pool is None:
        fail("make_pool(n, seed) returned None. Did you forget `return Pool(families, arrows)`?")
    if not hasattr(pool, "families") or not hasattr(pool, "arrows"):
        fail("make_pool(n, seed) must return a Pool (something with .families and .arrows).")
    return pool


def t_shape():
    pool = make(20, 1)
    if not isinstance(pool.families, list):
        fail(f"pool.families should be a list, but it is a {type(pool.families).__name__}.")
    if len(pool.families) != 20:
        fail(f"make_pool(20, 1) made {len(pool.families)} families. It should make exactly 20.\n"
             f"Tip: keep drawing families in a while loop until you have n that need a swap.")
    ids = [family.id for family in pool.families]
    if ids != list(range(1, 21)):
        fail(f"Family ids should be 1, 2, ..., 20 in order. They are {ids}.\n"
             f"Tip: give each new family the id len(families) + 1.")
    for family in pool.families:
        if family.patient_blood not in BLOOD_GROUPS or family.donor_blood not in BLOOD_GROUPS:
            fail(f"Family {family.id} has blood groups ({family.patient_blood!r}, {family.donor_blood!r}). "
                 f"Each must be one of 'O', 'A', 'B', 'AB'.")
    if not isinstance(pool.arrows, set):
        fail(f"pool.arrows should be a set of (i, j) tuples, but it is a {type(pool.arrows).__name__}.")


def t_arrows_valid():
    pool = make(40, 2)
    by_id = {family.id: family for family in pool.families}
    for arrow in pool.arrows:
        if not isinstance(arrow, tuple) or len(arrow) != 2:
            fail(f"Every arrow must be a tuple (i, j). Found {arrow!r}.")
        i, j = arrow
        if i == j:
            fail(f"Arrow {arrow} points a family at itself. Skip i == j when you draw arrows.")
        if i not in by_id or j not in by_id:
            fail(f"Arrow {arrow} uses an id that is not in the pool.")
        if not blood_ok(by_id[i].donor_blood, by_id[j].patient_blood):
            fail(f"Arrow {arrow} means family {i}'s donor ({by_id[i].donor_blood}) gives to family {j}'s "
                 f"patient ({by_id[j].patient_blood}), but the blood groups don't match.\n"
                 f"Check you used donor of i and patient of j, in that order.")
    if len(pool.arrows) == 0:
        fail("A 40-family pool has no arrows at all. Did you forget to add arrows to the set?")


def t_same_seed():
    def snapshot(pool):
        return ([(f.id, f.patient_blood, f.donor_blood) for f in pool.families], sorted(pool.arrows))
    if snapshot(make(30, 5)) != snapshot(make(30, 5)):
        fail("make_pool(30, 5) gave a different pool the second time. The same seed must give the same pool.\n"
             "Tip: create rng = random.Random(seed) at the start and use rng.random() / rng.choices() "
             "everywhere inside make_pool.")
    if snapshot(make(30, 5)) == snapshot(make(30, 6)):
        fail("make_pool(30, 5) and make_pool(30, 6) gave the same pool. Are you using the seed at all?")


def t_tissue_rate():
    pool = make(200, 3)
    chance = get(pool_module, "TISSUE_PASS_CHANCE")
    blood_matches = 0
    for giver in pool.families:
        for receiver in pool.families:
            if giver.id != receiver.id and blood_ok(giver.donor_blood, receiver.patient_blood):
                blood_matches += 1
    share = len(pool.arrows) / blood_matches
    if abs(share - chance) > 0.03:
        fail(f"Out of {blood_matches} blood-compatible (i, j) pairs, {len(pool.arrows)} became arrows "
             f"({share:.2f}).\nThat should be close to TISSUE_PASS_CHANCE = {chance}.\n"
             f"Each blood-compatible pair should get one random tissue roll: "
             f"if rng.random() < TISSUE_PASS_CHANCE, add the arrow.")


def t_who_joins():
    pool = make(500, 4)
    own_blood_ok = [f for f in pool.families if blood_ok(f.donor_blood, f.patient_blood)]
    share = len(own_blood_ok) / len(pool.families)
    if share == 0:
        fail("No family has a blood-compatible own donor. Families whose blood matches but whose tissue "
             "test fails\nshould join the pool too (without them no 3-way ring can ever form).")
    if share > 0.5:
        fail(f"{share:.0%} of families could give to their own patient by blood. Most families should be "
             f"blood mismatches.\nA blood-compatible family only joins if its own tissue roll FAILS "
             f"(rng.random() >= TISSUE_PASS_CHANCE).")


def t_speed():
    _, seconds = timed(make, 100, 0)
    if seconds > 2:
        fail(f"make_pool(100, 0) took {seconds:.1f} seconds. It should take well under 2 seconds.")


check("constants BLOOD_GROUPS, INDIA_BLOOD_MIX, TISSUE_PASS_CHANCE", t_constants)
check("can_give(donor, patient) follows the blood rules", t_can_give)
check("Family(id, patient_blood, donor_blood) stores its three values", t_family)
check("Pool(families, arrows) stores .families and .arrows", t_pool_class)
check("make_pool(20, 1) makes 20 families with ids 1..20", t_shape)
check("every arrow is blood-compatible, between two different families", t_arrows_valid)
check("same seed -> same pool, different seed -> different pool", t_same_seed)
check("about TISSUE_PASS_CHANCE of blood-compatible pairs become arrows", t_tissue_rate)
check("the right families join the pool", t_who_joins)
check("make_pool(100, 0) is fast", t_speed)
finish()
