from data import CATALOG

def interpret(message: str):
    message = message.lower()

    action = "add"
    if "remove" in message:
        action = "remove"

    quantity = 1

    for num, word in [
        (2, "two"),
        (3, "three"),
        (4, "four"),
    ]:
        if word in message:
            quantity = num

    item = None

    for name in CATALOG:
        if name in message:
            item = name
            break

    modifiers = []

    if "large" in message:
        modifiers.append("large")

    if "oat" in message:
        modifiers.append("oat_milk")

    if "extra shot" in message:
        modifiers.append("extra_shot")

    return {
        "action": action,
        "item": item,
        "quantity": quantity,
        "modifiers": modifiers,
    }