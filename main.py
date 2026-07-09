from fastapi import FastAPI
from models import ChatRequest
from order_manager import get_order, add_item, remove_item
from pricing import calculate_total
from llm import interpret

app = FastAPI()


@app.post("/chat")
def chat(req: ChatRequest):

    order = get_order(req.session_id)

    action = interpret(req.message)

    if action["action"] == "add" and action["item"]:
        add_item(order, action)

    elif action["action"] == "remove":
        remove_item(order, action["item"])

    total, discounts = calculate_total(order)

    return {
        "order": order,
        "discounts": discounts,
        "total": total
    }