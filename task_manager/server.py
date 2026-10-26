"""In-memory gRPC Task Manager server."""
import os
import threading
import time
from concurrent import futures

import grpc
from google.protobuf import empty_pb2

import task_manager_pb2
import task_manager_pb2_grpc

VALID_STATUSES = {"pending", "in_progress", "done"}


class TaskService(task_manager_pb2_grpc.TaskServiceServicer):
    def __init__(self):
        self._tasks = {}
        self._next_id = 1
        self._lock = threading.Lock()
        # Set this to 2 to demonstrate the client's one-second deadline handling.
        self.get_delay_seconds = float(os.getenv("TASK_MANAGER_GET_DELAY_SECONDS", "0"))

    def CreateTask(self, request, context):
        with self._lock:
            task = task_manager_pb2.Task(
                id=self._next_id, title=request.title, status="pending"
            )
            self._tasks[task.id] = task
            self._next_id += 1
            return task

    def GetTask(self, request, context):
        if request.id < 1:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "task id must be at least 1")
        if self.get_delay_seconds:
            time.sleep(self.get_delay_seconds)
        with self._lock:
            task = self._tasks.get(request.id)
            if task is None:
                context.abort(grpc.StatusCode.NOT_FOUND, f"task {request.id} not found")
            return task

    def ListTasks(self, request, context):
        del request
        with self._lock:
            tasks = [task_manager_pb2.Task(id=t.id, title=t.title, status=t.status)
                     for t in self._tasks.values()]
        for task in tasks:
            if not context.is_active():
                return
            yield task

    def _update(self, request, context):
        if request.id < 1:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "task id must be at least 1")
        if request.status not in VALID_STATUSES:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION,
                          "status must be pending, in_progress, or done")
        with self._lock:
            task = self._tasks.get(request.id)
            if task is None:
                context.abort(grpc.StatusCode.NOT_FOUND, f"task {request.id} not found")
            task.status = request.status
            return task_manager_pb2.Task(id=task.id, title=task.title, status=task.status)

    def UpdateTask(self, request, context):
        return self._update(request, context)

    def StreamTaskUpdates(self, request_iterator, context):
        for request in request_iterator:
            if not context.is_active():
                return
            yield self._update(request, context)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    task_manager_pb2_grpc.add_TaskServiceServicer_to_server(TaskService(), server)
    port = server.add_insecure_port("[::]:50051")
    if port == 0:
        raise RuntimeError("Could not bind gRPC server to port 50051")
    server.start()
    print(f"Task Manager gRPC server listening on port {port}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=2).wait()


if __name__ == "__main__":
    serve()
