Cafe Order Chatbot

A FastAPI backend that takes plain-English cafe orders across multiple chat turns, understands them via a local LLM (Ollama), and returns a structured order summary with pricing, combo discounts, and modifier validation.

How it works:
data.py — the menu, modifiers, and combo deals.
nlu_local.py — sends the message + current order to a local Ollama model with a JSON schema, and gets back structured operations (add/remove/modify/finalize/cancel) plus a natural-language reply.
order_manager.py — in-memory order state per session. Validates modifiers against the item's category before storing anything.
pricing.py — computes the total, applying combo discounts based on actual quantities on the order.
validators.py — shared modifier-validation logic used by both order_manager.py and pricing.py.
main.py — the FastAPI app that wires it all together.

Setup:
Install Ollama (free, runs locally, no API key): https://ollama.com/download
Pull a model:
bash
   ollama pull llama3.1

Make sure the Ollama app/service is running in the background. 

Install Python dependencies:
bash
   pip install fastapi uvicorn ollama pydantic
Running the server
bash
uvicorn main:app --reload

By default this starts the API at http://127.0.0.1:8000.

Opening that URL directly in a browser won't show anything — there's no root page. Instead, go to the interactive docs:

http://127.0.0.1:8000/docs

Expand POST /chat, click "Try it out", and send a request body like:

json
{
  "session_id": "test1",
  "message": "I'd like a latte and a croissant"
}

Each session_id keeps its own independent order — use a new one to start over, or send "message": "cancel my order" to clear an existing session.
