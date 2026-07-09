orders = {}

def get_order(session_id):
    if session_id not in orders:
        orders[session_id] = []

    return orders[session_id]


def add_item(order, action):
    order.append({
        "item": action["item"],
        "quantity": action["quantity"],
        "modifiers": action["modifiers"]
    })


def remove_item(order, item_name):
    order[:] = [
        item for item in order
        if item["item"] != item_name
    ]