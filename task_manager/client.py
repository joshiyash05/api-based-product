"""Example client exercising unary and streaming Task Manager RPCs."""
import grpc
from google.protobuf import empty_pb2

import task_manager_pb2
import task_manager_pb2_grpc


def display(task):
    print(f"Task(id={task.id}, title={task.title!r}, status={task.status})")


def update_requests():
    yield task_manager_pb2.UpdateTaskRequest(id=1, status="in_progress")
    yield task_manager_pb2.UpdateTaskRequest(id=2, status="done")
    yield task_manager_pb2.UpdateTaskRequest(id=3, status="in_progress")


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = task_manager_pb2_grpc.TaskServiceStub(channel)
        print("Creating three tasks:")
        for title in ("Write proposal", "Build prototype", "Review results"):
            display(stub.CreateTask(task_manager_pb2.CreateTaskRequest(title=title)))

        print("\nFetching task #2 (deadline: 1 second):")
        try:
            display(stub.GetTask(task_manager_pb2.GetTaskRequest(id=2), timeout=1.0))
        except grpc.RpcError as exc:
            if exc.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                print("The request timed out; continuing gracefully.")
            else:
                print(f"GetTask failed: {exc.code().name}: {exc.details()}")

        print("\nStreaming all tasks:")
        for task in stub.ListTasks(empty_pb2.Empty()):
            display(task)

        print("\nStreaming three task updates:")
        try:
            for task in stub.StreamTaskUpdates(update_requests()):
                display(task)
        except grpc.RpcError as exc:
            print(f"StreamTaskUpdates failed: {exc.code().name}: {exc.details()}")


if __name__ == "__main__":
    run()
