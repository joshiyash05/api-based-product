"""
rate_limiters.py
Standard library implementations of Token Bucket and Leaky Bucket algorithms.
"""

import time
import threading
import queue
from typing import Any, Callable, Optional


class TokenBucket:
    """
    Thread-safe Token Bucket Rate Limiter.
    Allows traffic bursts up to `capacity` while maintaining a long-term
    average rate of `refill_rate` tokens/second.
    """
    def __init__(self, capacity: float, refill_rate: float):
        if capacity <= 0 or refill_rate <= 0:
            raise ValueError("Capacity and refill rate must be positive numbers.")
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity)
        self.last_refill_timestamp = time.monotonic()
        self.lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill_timestamp
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill_timestamp = now

    def allow_request(self, tokens: float = 1.0) -> bool:
        """
        Check if `tokens` can be consumed.
        Returns True if permitted, False otherwise.
        """
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


class LeakyBucketMeter:
    """
    Thread-safe Leaky Bucket Rate Limiter (Traffic Metering).
    Requests add water to the bucket; water leaks at `leak_rate` per second.
    Rejects requests if adding water would exceed `capacity`.
    """
    def __init__(self, capacity: float, leak_rate: float):
        if capacity <= 0 or leak_rate <= 0:
            raise ValueError("Capacity and leak rate must be positive numbers.")
        self.capacity = float(capacity)
        self.leak_rate = float(leak_rate)
        self.water_level = 0.0
        self.last_leak_timestamp = time.monotonic()
        self.lock = threading.Lock()

    def _leak(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_leak_timestamp
        leaked_amount = elapsed * self.leak_rate
        self.water_level = max(0.0, self.water_level - leaked_amount)
        self.last_leak_timestamp = now

    def allow_request(self, amount: float = 1.0) -> bool:
        """
        Check if `amount` of water can be added.
        Returns True if permitted, False if bucket overflows.
        """
        with self.lock:
            self._leak()
            if self.water_level + amount <= self.capacity:
                self.water_level += amount
                return True
            return False


class LeakyBucketQueue:
    """
    Thread-safe Leaky Bucket Traffic Shaper (Queue variant).
    Buffers incoming items and processes them at a constant uniform rate.
    """
    def __init__(self, capacity: int, process_rate: float, processor_callback: Callable[[Any], None]):
        if capacity <= 0 or process_rate <= 0:
            raise ValueError("Capacity and process rate must be positive numbers.")
        self.capacity = capacity
        self.interval = 1.0 / process_rate
        self.queue = queue.Queue(maxsize=capacity)
        self.processor_callback = processor_callback
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start background worker thread."""
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def stop(self) -> None:
        """Stop background worker thread gracefully."""
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join()

    def enqueue(self, item: Any) -> bool:
        """
        Enqueue an item. Returns True if successfully queued, False if full.
        """
        try:
            self.queue.put_nowait(item)
            return True
        except queue.Full:
            return False

    def _worker(self) -> None:
        while self.running:
            try:
                item = self.queue.get(timeout=0.1)
                self.processor_callback(item)
                self.queue.task_done()
                time.sleep(self.interval)
            except queue.Empty:
                continue