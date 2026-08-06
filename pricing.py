from data import CATALOG, COMBOS, MODIFIERS
from validators import split_valid_modifiers


def calculate_total(order):
    total = 0.0
    warnings = []
    item_quantities = {}  # item name -> total quantity across all lines

    for line in order:
        item = line["item"]
        qty = line["quantity"]

        valid_mods, invalid_mods = split_valid_modifiers(item, line["modifiers"])
        if invalid_mods:
            verb = "was" if len(invalid_mods) == 1 else "were"
            warnings.append(
                f"{', '.join(invalid_mods)} {verb} ignored on {item} (not applicable)."
            )

        price = CATALOG[item]["price"] + sum(MODIFIERS[m]["price"] for m in valid_mods)
        total += price * qty
        item_quantities[item] = item_quantities.get(item, 0) + qty

    discounts = []
    for combo in COMBOS.values():
        required_counts = [item_quantities.get(i, 0) for i in combo["items"]]
        times = min(required_counts) if required_counts else 0
        if times > 0:
            total -= combo["discount"] * times
            label = combo["label"] if times == 1 else f"{combo['label']} x{times}"
            discounts.append(label)

    return round(total, 2), discounts, warnings