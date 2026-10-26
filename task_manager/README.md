# gRPC Task Manager

An in-memory Python gRPC service. Run commands from this directory.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. task_manager.proto
```

Start the service in one terminal:

```powershell
python server.py
```

Run the example client in another terminal:

```powershell
python client.py
```

The client creates three tasks, requests task #2 with a one-second deadline,
streams the task list, and sends three bidirectional task updates. To exercise
the timeout path, start the server with a two-second delay before `GetTask`:

```powershell
$env:TASK_MANAGER_GET_DELAY_SECONDS = "2"
python server.py
```

The client catches `DEADLINE_EXCEEDED` and continues to the streaming examples.
The service validates statuses (`pending`, `in_progress`, `done`), returns
`INVALID_ARGUMENT` for IDs below 1, `NOT_FOUND` for missing tasks, and
`FAILED_PRECONDITION` for invalid statuses. Tasks are stored in memory and are
cleared when the server stops.
