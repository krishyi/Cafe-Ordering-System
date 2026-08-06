from data import CATALOG, MODIFIERS

def split_valid_modifiers(item, modifiers):
    """Split modifier keys into (valid, invalid) for this item's category."""
    category = CATALOG[item]["category"]
    valid, invalid = [], []
    for m in modifiers:
        if m in MODIFIERS and category in MODIFIERS[m]["applies_to"]:
            valid.append(m)
        else:
            invalid.append(m)
    return valid, invalid
