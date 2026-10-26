# Order API with MCP and Kong

This project provides an in-memory JSON Order API, an MCP stdio server exposing one `order_api` tool, and a DB-less Kong Gateway configured with a 5-request-per-minute per-client-IP limit. It runs as a Docker Compose stack, which is suitable for a small Rocky Linux host with Docker Engine and the Compose plugin.

## Rocky Linux setup

Install Docker Engine and the Compose plugin using Docker's current RPM repository instructions for CentOS/RHEL-compatible systems: https://docs.docker.com/engine/install/centos/ and https://docs.docker.com/compose/install/linux/. On a Rocky host where Docker's CentOS repository is appropriate, the usual package/start steps are:

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker compose version
```

Copy or clone this folder onto the server, then run from `mcp_server/`:

```bash
sudo docker compose up --build -d
sudo docker compose ps
```

Kong listens on host port 8000 and proxies `/api/orders` and `/api/orders/{id}` to the API container. The API itself is only exposed on the internal Compose network. Open TCP/8000 in the host firewall only if clients need remote access, and restrict the source addresses as appropriate. Do not expose Kong's Admin API (port 8001) publicly.

## REST API

```bash
curl -i -H 'Content-Type: application/json' \
  -d '{"item":"book","quantity":2}' http://127.0.0.1:8000/api/orders
curl -i http://127.0.0.1:8000/api/orders/1
curl -i http://127.0.0.1:8000/api/orders
```

Orders are held in process memory and reset when the API container is recreated. Creation returns 201; invalid JSON or non-positive quantity returns 422; an unknown ID returns 404.

## Rate-limit evidence

Run the demonstration from the host. It sends six GET requests through Kong and records status codes in `rate_limit_demo.log`:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install httpx
python demo_rate_limit.py | tee rate_limit_demo.log
```

Expected result: requests 1–5 return HTTP 200 and request 6 returns HTTP 429. The committed script prints the response `RateLimit-Remaining` header when present. `policy: local` stores counters in Kong's memory, which is suitable for this single-node assignment deployment; counters are not shared across multiple gateway nodes. See Kong's rate limiting documentation: https://developer.konghq.com/plugins/rate-limiting/.

## MCP server

Install Python 3.10+ and the project dependencies on the machine running the MCP client/server:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
ORDER_API_BASE_URL=http://127.0.0.1:8000/api python mcp_server.py
```

The stdio MCP server exposes `order_api` with actions `create_order`, `get_order`, and `list_orders`. It validates action-specific input, calls Kong, and returns the upstream JSON body. The JSON Schema artifact is in `order_api_schema.json`; FastMCP publishes the corresponding typed tool schema from the server function. Keep stdout reserved for MCP protocol traffic when configuring an MCP client.

## Configuration files

- `order_api.py`: FastAPI backend
- `mcp_server.py`: MCP stdio server and `order_api` tool
- `order_api_schema.json`: tool input schema
- `kong.yml`: declarative Kong service, route, and rate-limit plugin
- `docker-compose.yml` and `Dockerfile`: single-host runtime
- `demo_rate_limit.py`: six-request proof script
