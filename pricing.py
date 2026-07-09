from data import CATALOG, MODIFIERS, COMBOS

def calculate_total(order):

    total = 0

    items = []

    for order_item in order:

        price = CATALOG[order_item["item"]]["price"]

        items.append(order_item["item"])

        for modifier in order_item["modifiers"]:
            price += MODIFIERS[modifier]["price"]

        total += price * order_item["quantity"]

    discounts = []

    if "latte" in items and "croissant" in items:
        total -= COMBOS["breakfast_deal"]["discount"]
        discounts.append(COMBOS["breakfast_deal"]["label"])

    if "espresso" in items and "muffin" in items:
        total -= COMBOS["coffee_and_snack"]["discount"]
        discounts.append(COMBOS["coffee_and_snack"]["label"])

    return round(total, 2), discounts