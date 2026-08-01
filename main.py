from fastapi import FastAPI
from data import CATALOG
from models import ChatRequest, ChatResponse
from order_manager import get_order, add_item, remove_item, modify_item
from pricing import calculate_total
from nlu_local import interpret  # local/free — swap back to `from llm import interpret` if you get API credits later

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    order = get_order(req.session_id)

    result = interpret(req.message, order)

    for op in result.get("operations", []):
        op_type = op.get("type")

        if op_type == "add" and op.get("item") in CATALOG:
            add_item(
                req.session_id,
                order,
                op["item"],
                op.get("quantity") or 1,
                op.get("modifiers") or [],
            )

        elif op_type == "remove":
            remove_item(
                order,
                target_line_id=op.get("target_line_id"),
                item=op.get("item"),
                quantity=op.get("quantity"),
            )

        elif op_type == "modify":
            modify_item(
                order,
                target_line_id=op.get("target_line_id"),
                item=op.get("item"),
                set_quantity=op.get("set_quantity"),
                add_modifiers=op.get("modifiers"),
                remove_modifiers=op.get("remove_modifiers"),
            )

    total, discounts, warnings = calculate_total(order)

    return {
        "reply": result.get("reply", ""),
        "message_type": result.get("message_type"),
        "order": order,
        "discounts": discounts,
        "warnings": warnings,
        "total": total,
    }