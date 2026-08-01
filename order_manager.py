from itertools import count
from typing import Dict, List, Optional

_orders: Dict[str, List[dict]] = {}
_id_counters: Dict[str, "count"] = {}
def get_order(session_id: str) -> List[dict]:
    if session_id not in _orders:
        _orders[session_id] = []
        _id_counters[session_id] = count(1)
    return _orders[session_id]

def _next_id(session_id: str) -> int:
    return next(_id_counters[session_id])

def find_line(order: List[dict], line_id: int) -> Optional[dict]:
    for line in order:
        if line["id"] == line_id:
            return line
    return None

def add_item(session_id: str, order: List[dict], item: str, quantity: int, modifiers: List[str]) -> dict:
    quantity = max(1, quantity or 1)
    modifiers = modifiers or []
    modifiers_key = sorted(modifiers)

    for line in order:
        if line["item"] == item and sorted(line["modifiers"]) == modifiers_key:
            line["quantity"] += quantity
            return line

    new_line = {
        "id": _next_id(session_id),
        "item": item,
        "quantity": quantity,
        "modifiers": list(modifiers),
    }
    order.append(new_line)
    return new_line

def _resolve_line(order: List[dict], target_line_id: Optional[int], item: Optional[str]) -> Optional[dict]:
    if target_line_id is not None:
        line = find_line(order, target_line_id)
        if line is not None:
            return line
    if item is not None:
        matches = [l for l in order if l["item"] == item]
        if matches:
            return matches[-1]
    return None

def remove_item(
    order: List[dict],
    target_line_id: Optional[int] = None,
    item: Optional[str] = None,
    quantity: Optional[int] = None,
) -> bool:
    line = _resolve_line(order, target_line_id, item)

    if line is None:
        return False

    if quantity is None or quantity >= line["quantity"]:
        order.remove(line)
    else:
        line["quantity"] -= quantity
    return True

def modify_item(
    order: List[dict],
    target_line_id: Optional[int] = None,
    item: Optional[str] = None,
    set_quantity: Optional[int] = None,
    add_modifiers: Optional[List[str]] = None,
    remove_modifiers: Optional[List[str]] = None,
) -> bool:
    line = _resolve_line(order, target_line_id, item)
    if line is None:
        return False

    if set_quantity is not None and set_quantity > 0:
        line["quantity"] = set_quantity

    if add_modifiers:
        for m in add_modifiers:
            if m not in line["modifiers"]:
                line["modifiers"].append(m)

    if remove_modifiers:
        line["modifiers"] = [m for m in line["modifiers"] if m not in remove_modifiers]

    return True