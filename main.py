from fastapi import FastAPI

from data import CATALOG
from models import ChatRequest, ChatResponse
from order_manager import (
    get_order,
    add_item,
    remove_item,
    modify_item,
    clear_order,
    is_finalized,
    set_finalized,
)
from pricing import calculate_total
from nlu_local import interpret

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    order = get_order(req.session_id)
    result = interpret(req.message, order)
    msg_type = result.get("message_type")
    warnings = []

    if msg_type == "cancel":
        clear_order(req.session_id, order)
    else:
        for op in result.get("operations", []):
            op_type = op.get("type")

            if op_type == "add" and op.get("item") in CATALOG:
                _, invalid_mods = add_item(
                    req.session_id,
                    order,
                    op["item"],
                    op.get("quantity") or 1,
                    op.get("modifiers") or [],
                )
                if invalid_mods:
                    warnings.append(f"{', '.join(invalid_mods)} not valid on {op['item']} - ignored.")

            elif op_type == "remove":
                remove_item(
                    order,
                    target_line_id=op.get("target_line_id"),
                    item=op.get("item"),
                    quantity=op.get("quantity"),
                )

            elif op_type == "modify":
                _, invalid_mods = modify_item(
                    order,
                    target_line_id=op.get("target_line_id"),
                    item=op.get("item"),
                    set_quantity=op.get("set_quantity"),
                    add_modifiers=op.get("modifiers"),
                    remove_modifiers=op.get("remove_modifiers"),
                )
                if invalid_mods:
                    warnings.append(f"{', '.join(invalid_mods)} not valid - ignored.")

        if msg_type == "finalize":
            set_finalized(req.session_id, True)
        elif result.get("operations"):
            # any real edit reopens a previously finalized order
            set_finalized(req.session_id, False)

    total, discounts, price_warnings = calculate_total(order)
    warnings += price_warnings

    reply = result.get("reply", "")
    if msg_type == "finalize":
        # Never trust the model's own stated dollar figure - it has no
        # access to pricing logic and can (and did, in testing) just make
        # one up. Always state the real, server-computed total instead.
        reply = f"Thanks, that's everything! Your total comes to ${total:.2f}."

    return {
        "reply": reply,
        "message_type": msg_type,
        "finalized": is_finalized(req.session_id),
        "order": order,
        "discounts": discounts,
        "warnings": warnings,
        "total": total,
    }