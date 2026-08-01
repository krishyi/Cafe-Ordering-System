"""
Setup: install Ollama (ollama.com/download), `ollama pull llama3.1`,
`pip install ollama`. No API key needed - just have the Ollama app running.
"""

import os
from typing import List, Literal, Optional
import ollama
from pydantic import BaseModel, Field
from data import CATALOG, COMBOS, MODIFIERS

MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

_CATALOG_KEYS = list(CATALOG.keys())
_MODIFIER_KEYS = list(MODIFIERS.keys())

class Operation(BaseModel):
    type: Literal["add", "remove", "modify"]
    item: Optional[str] = Field(
        default=None,
        description="Catalog item key. Required for 'add'. Optional for remove/modify if target_line_id is set.",
    )
    quantity: Optional[int] = Field(
        default=None,
        description="add: how many to add. remove: how many units to take off (omit to remove the whole line).",
    )
    modifiers: Optional[List[str]] = Field(
        default=None, description="add: modifiers on the new line. modify: modifiers to ADD."
    )
    remove_modifiers: Optional[List[str]] = Field(
        default=None, description="modify only: modifiers to strip off the line."
    )
    set_quantity: Optional[int] = Field(
        default=None, description="modify only: new absolute quantity for the line."
    )
    target_line_id: Optional[int] = Field(
        default=None, description="id of the existing order line this remove/modify refers to."
    )


class ProcessOrder(BaseModel):
    message_type: Literal["order_action", "question", "chitchat", "clarify"]
    reply: str
    operations: List[Operation] = Field(default_factory=list)


def _catalog_block():
    items = "\n".join(f"- {name}: ${info['price']:.2f} ({info['category']})" for name, info in CATALOG.items())
    mods = "\n".join(
        f"- {name}: +${info['price']:.2f} (only valid on: {', '.join(info['applies_to'])})"
        for name, info in MODIFIERS.items()
    )
    combos = "\n".join(
        f"- {c['label']}: {' + '.join(c['items'])} -> ${c['discount']:.2f} off"
        for c in COMBOS.values()
    )
    return f"MENU:\n{items}\n\nMODIFIERS:\n{mods}\n\nDEALS:\n{combos}"


def _order_block(order):
    if not order:
        return "CURRENT ORDER: (empty)"
    lines = []
    for line in order:
        mods = f" [{', '.join(line['modifiers'])}]" if line["modifiers"] else ""
        lines.append(f"- id={line['id']}: {line['quantity']}x {line['item']}{mods}")
    return "CURRENT ORDER:\n" + "\n".join(lines)


SYSTEM_PROMPT = (
    "You are the order-parsing layer for a cafe ordering chatbot. Given the "
    "customer's latest message and the current order, respond with ONLY a "
    "JSON object matching the required schema - no prose, no markdown fences.\n\n"
    "Rules:\n"
    "- A message can mention several items ('a latte and a croissant') -> "
    "emit one 'add' operation per distinct item.\n"
    "- Understand quantity words/phrases naturally: digits, number words, "
    "'a couple' (2), 'a few' (3), 'another X' (add 1 more X), etc.\n"
    "- Item values in operations must be one of: " + ", ".join(_CATALOG_KEYS) + "\n"
    "- Modifier values must be one of: " + ", ".join(_MODIFIER_KEYS) + "\n"
    "- For remove/modify, resolve which existing line the customer means "
    "using CURRENT ORDER and set target_line_id. Only use message_type "
    "'clarify' (empty operations, ask in reply) if it's truly ambiguous "
    "which line they mean.\n"
    "- Still emit modifier requests even if invalid for that item's category "
    "(e.g. oat milk on a sandwich) - a separate pricing step enforces "
    "validity - but you may mention the issue in your reply.\n"
    "- Questions about the menu, prices, or deals -> message_type 'question', "
    "answer directly from the menu below, operations empty.\n"
    "- Greetings/thanks/small talk -> message_type 'chitchat', operations empty.\n"
    "- Always fill 'reply' with a short, friendly response confirming what "
    "was done or answering the question.\n\n"
    f"{_catalog_block()}"
)


def _fallback():
    return {
        "message_type": "chitchat",
        "reply": "Sorry, I didn't catch that - could you rephrase?",
        "operations": [],
    }


def _sanitize(parsed: dict) -> dict:
    clean_ops = []
    dropped_notes = []

    for op in parsed.get("operations", []):
        op_type = op.get("type")
        item = op.get("item")

        if item is not None and item not in CATALOG:
            if op_type == "add":
                dropped_notes.append(item)
                continue
            op["item"] = None

        if op.get("modifiers"):
            op["modifiers"] = [m for m in op["modifiers"] if m in MODIFIERS]
        if op.get("remove_modifiers"):
            op["remove_modifiers"] = [m for m in op["remove_modifiers"] if m in MODIFIERS]

        clean_ops.append(op)

    parsed["operations"] = clean_ops
    if dropped_notes:
        parsed["reply"] = (
            parsed.get("reply", "").rstrip()
            + f" (Sorry, I didn't recognize: {', '.join(dropped_notes)}.)"
        ).strip()
    return parsed

def interpret(message: str, order):
    user_content = f"{_order_block(order)}\n\nCUSTOMER MESSAGE: {message}"

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            format=ProcessOrder.model_json_schema(),
            options={"temperature": 0},
        )
        raw = response["message"]["content"]
        parsed = ProcessOrder.model_validate_json(raw)
        return _sanitize(parsed.model_dump())
    except Exception as exc:
        print(f"[llm.interpret] falling back due to: {exc}")
        return _fallback()