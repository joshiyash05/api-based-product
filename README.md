# Assignment Projects

This repository contains three standalone Python projects. Each project has its own source files and run instructions.

## Projects

### Order API with MCP and Kong

An in-memory REST API for creating, listing, and retrieving orders; an MCP server that exposes the API as the `order_api` tool; and a declarative Kong Gateway setup with a limit of five requests per minute. The project includes a six-request demo for producing rate-limit evidence.

- Project files and Rocky Linux setup: [mcp_server/README.md](mcp_server/README.md)
- API: [mcp_server/order_api.py](mcp_server/order_api.py)
- MCP server: [mcp_server/mcp_server.py](mcp_server/mcp_server.py)
- MCP input schema: [mcp_server/order_api_schema.json](mcp_server/order_api_schema.json)
- Kong configuration: [mcp_server/kong.yml](mcp_server/kong.yml)

Start its API and gateway from the project directory:

```bash
cd mcp_server
sudo docker compose up --build -d
```

Follow the project README to install Python dependencies, run the MCP stdio server, and save the rate-limit demonstration output.

### gRPC Task Manager

An in-memory gRPC service that creates, retrieves, lists, and updates tasks. It demonstrates unary calls, server streaming, bidirectional streaming, status validation, and client deadlines.

- Setup and usage: [task_manager/README.md](task_manager/README.md)
- Server: [task_manager/server.py](task_manager/server.py)
- Example client: [task_manager/client.py](task_manager/client.py)

Run the setup and protocol generation commands in `task_manager/README.md`, then start the server and client in separate terminals.

### Python Rate Limiters

Thread-safe Token Bucket and Leaky Bucket implementations, with a runnable demonstration and unit tests.

- Setup and usage: [rate_limiter_project/README.md](rate_limiter_project/README.md)
- Implementations: [rate_limiter_project/rate_limiters.py](rate_limiter_project/rate_limiters.py)
- Demo: [rate_limiter_project/demo.py](rate_limiter_project/demo.py)

Run from the project directory:

```bash
cd rate_limiter_project
python demo.py
python -m unittest test_rate_limiters.py
```

## Requirements

- Python 3.10 or newer for the Order API/MCP project; see its README for Python packages and Docker Compose instructions.
- Python and the packages listed in `task_manager/requirements.txt` for the gRPC project.
- Python 3.10 or newer for the rate-limiter project; it uses only the standard library.

The projects are independent. Run commands from the relevant project directory and follow that directory's README for environment setup.

## Assignment reference

[Assignment.pdf](Assignment.pdf) is included as the original assignment reference.
