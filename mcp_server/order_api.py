"""In-memory REST API for orders."""
from threading import Lock

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Order API", version="1.0.0")
_orders: dict[int, dict] = {}
_next_id = 1
_lock = Lock()


class OrderInput(BaseModel):
    item: str = Field(min_length=1, strict=True)
    quantity: int = Field(gt=0, strict=True)


@app.post("/orders", status_code=201)
def create_order(payload: OrderInput):
    global _next_id
    with _lock:
        order = {"id": _next_id, "item": payload.item, "quantity": payload.quantity, "status": "created"}
        _orders[_next_id] = order
        _next_id += 1
        return order


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id < 1:
        raise HTTPException(status_code=400, detail="id must be a positive integer")
    order = _orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order


@app.get("/orders")
def list_orders():
    return list(_orders.values())

