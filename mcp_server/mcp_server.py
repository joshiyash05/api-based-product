"""MCP stdio server exposing the Order API as the order_api tool."""
import os
from typing import Literal

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Order API")
API_BASE_URL = os.getenv("ORDER_API_BASE_URL", "http://127.0.0.1:8000/api")


@mcp.tool()
async def order_api(action: Literal["create_order", "get_order", "list_orders"], item: str | None = None, quantity: int | None = None,
                    order_id: int | None = None) -> dict | list:
    """Call the Order API. Actions: create_order(item, quantity), get_order(order_id), list_orders()."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10) as client:
        if action == "create_order":
            if not isinstance(item, str) or not item.strip():
                raise ValueError("item must be a non-empty string")
            if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("quantity must be a positive integer")
            response = await client.post("/orders", json={"item": item, "quantity": quantity})
        elif action == "get_order":
            if isinstance(order_id, bool) or not isinstance(order_id, int) or order_id < 1:
                raise ValueError("order_id must be a positive integer")
            response = await client.get(f"/orders/{order_id}")
        elif action == "list_orders":
            response = await client.get("/orders")
        else:
            raise ValueError("action must be create_order, get_order, or list_orders")
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    mcp.run(transport="stdio")


