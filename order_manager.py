from itertools import count
from typing import Dict, List, Optional

from validators import split_valid_modifiers

_orders: Dict[str, List[dict]] = {}
_id_counters: Dict[str, "count"] = {}
_finalized: Dict[str, bool] = {}


def get_order(session_id: str) -> List[dict]:
    if session_id not in _orders:
        _orders[session_id] = []
        _id_counters[session_id] = count(1)
        _finalized[session_id] = False
    return _orders[session_id]


def _next_id(session_id: str) -> int:
    return next(_id_counters[session_id])


def find_line(order: List[dict], line_id: int) -> Optional[dict]:
    for line in order:
        if line["id"] == line_id:
            return line
    return None


def _resolve_line(order: List[dict], target_line_id: Optional[int], item: Optional[str]) -> Optional[dict]:
    """Find the order line a remove/modify operation refers to: prefer the
    explicit line id, fall back to the most recently added line matching
    the item name if the id wasn't given."""
    if target_line_id is not None:
        line = find_line(order, target_line_id)
        if line is not None:
            return line
    if item is not None:
        matches = [l for l in order if l["item"] == item]
        if matches:
            return matches[-1]
    return None


def add_item(session_id: str, order: List[dict], item: str, quantity: int, modifiers: List[str]):
    """Returns (line, invalid_modifiers) - invalid_modifiers were dropped,
    not stored."""
    quantity = max(1, quantity or 1)
    valid_mods, invalid_mods = split_valid_modifiers(item, modifiers or [])
    modifiers_key = sorted(valid_mods)

    for line in order:
        if line["item"] == item and sorted(line["modifiers"]) == modifiers_key:
            line["quantity"] += quantity
            return line, invalid_mods

    new_line = {
        "id": _next_id(session_id),
        "item": item,
        "quantity": quantity,
        "modifiers": valid_mods,
    }
    order.append(new_line)
    return new_line, invalid_mods


def remove_item(
        order: List[dict],
        target_line_id: Optional[int] = None,
        item: Optional[str] = None,
        quantity: Optional[int] = None,
) -> bool:
    """Remove `quantity` units from one specific line. If quantity is None
    or >= the line's quantity, the whole line is dropped."""
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
):
    """Returns (success, invalid_modifiers) - invalid_modifiers were
    requested via add_modifiers but dropped, not stored."""
    line = _resolve_line(order, target_line_id, item)
    if line is None:
        return False, []

    if set_quantity is not None and set_quantity > 0:
        line["quantity"] = set_quantity

    invalid_mods = []
    if add_modifiers:
        valid_mods, invalid_mods = split_valid_modifiers(line["item"], add_modifiers)
        for m in valid_mods:
            if m not in line["modifiers"]:
                line["modifiers"].append(m)

    if remove_modifiers:
        line["modifiers"] = [m for m in line["modifiers"] if m not in remove_modifiers]

    return True, invalid_mods


def is_finalized(session_id: str) -> bool:
    return _finalized.get(session_id, False)


def set_finalized(session_id: str, value: bool) -> None:
    _finalized[session_id] = value


def clear_order(session_id: str, order: List[dict]) -> None:
    order.clear()
    _finalized[session_id] = False