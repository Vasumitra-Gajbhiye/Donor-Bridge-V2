"""Generate simulated families and compatibility arrows for the exchange pool."""

import random


BLOOD_GROUPS = ["O", "A", "B", "AB"]

# Agrawal et al. (2014), 10,000 Indian donors, Table 2; DOI: 10.4103/0973-6247.137452.
# The study reports O 37.12%, A 22.88%, B 32.26%, and AB 7.74%.
INDIA_BLOOD_MIX = {"O": 0.3712, "A": 0.2288, "B": 0.3226, "AB": 0.0774}

# docs/original_plan.md: unrelated-pair crossmatch is positive about 11% of the time.
TISSUE_PASS_CHANCE = 0.89

GIVES_TO = {
    "O": ["O", "A", "B", "AB"],
    "A": ["A", "AB"],
    "B": ["B", "AB"],
    "AB": ["AB"],
}


def can_give(donor, patient):
    """Return whether the donor's blood group is compatible with the patient."""
    return patient in GIVES_TO[donor]


class Family:
    """One patient and their willing donor."""

    def __init__(self, id, patient_blood, donor_blood):
        self.id = id
        self.patient_blood = patient_blood
        self.donor_blood = donor_blood


class Pool:
    """A collection of families and directed compatibility arrows between them."""

    def __init__(self, families, arrows):
        self.families = families
        self.arrows = arrows


def make_pool(n, seed):
    """Generate exactly n families that need an exchange, plus their arrows."""
    if n < 0:
        raise ValueError("n must be zero or greater")

    rng = random.Random(seed)
    groups = list(INDIA_BLOOD_MIX.keys())
    weights = list(INDIA_BLOOD_MIX.values())

    families = []
    while len(families) < n:
        patient = rng.choices(groups, weights)[0]
        donor = rng.choices(groups, weights)[0]

        # A family joins when its donor cannot already donate to its own patient.
        # If blood works, a failed tissue test is also enough to need an exchange.
        if not can_give(donor, patient):
            families.append(Family(len(families) + 1, patient, donor))
        elif rng.random() >= TISSUE_PASS_CHANCE:
            families.append(Family(len(families) + 1, patient, donor))

    arrows = set()
    for family_i in families:
        for family_j in families:
            if family_i.id == family_j.id:
                continue
            if can_give(family_i.donor_blood, family_j.patient_blood):
                if rng.random() < TISSUE_PASS_CHANCE:
                    arrows.add((family_i.id, family_j.id))

    return Pool(families, arrows)


if __name__ == "__main__":
    example_pool = make_pool(6, seed=1)
    print("Families:")
    for family in example_pool.families:
        print(
            f"  {family.id}: patient {family.patient_blood}, "
            f"donor {family.donor_blood}"
        )
    print("Compatibility arrows:")
    print(sorted(example_pool.arrows))
