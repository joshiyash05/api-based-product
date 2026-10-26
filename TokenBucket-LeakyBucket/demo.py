"""
demo.py
Script to demonstrate Token Bucket and Leaky Bucket usage.
"""

import time
from rate_limiters import TokenBucket, LeakyBucketMeter, LeakyBucketQueue


def demo_token_bucket():
    print("========================================")
    print("         TOKEN BUCKET DEMO              ")
    print("========================================")
    # Capacity = 3, Refill Rate = 1 token/sec
    tb = TokenBucket(capacity=3, refill_rate=1)

    print("--> Sending 5 immediate requests (Capacity: 3):")
    for i in range(1, 6):
        allowed = tb.allow_request()
        print(f"  Request {i}: {'[ALLOWED]' if allowed else '[BLOCKED]'}")

    print("\n--> Sleeping for 2 seconds to refill 2 tokens...")
    time.sleep(2)

    print("--> Sending 3 subsequent requests:")
    for i in range(6, 9):
        allowed = tb.allow_request()
        print(f"  Request {i}: {'[ALLOWED]' if allowed else '[BLOCKED]'}")


def demo_leaky_bucket_meter():
    print("\n========================================")
    print("      LEAKY BUCKET (METER) DEMO         ")
    print("========================================")
    # Capacity = 3 units, Leak Rate = 1 unit/sec
    lb = LeakyBucketMeter(capacity=3, leak_rate=1)

    print("--> Sending 5 immediate requests (Capacity: 3):")
    for i in range(1, 6):
        allowed = lb.allow_request()
        print(f"  Request {i}: {'[ALLOWED]' if allowed else '[BLOCKED]'}")

    print("\n--> Sleeping for 2 seconds to leak 2 units of water...")
    time.sleep(2)

    print("--> Sending 2 subsequent requests:")
    for i in range(6, 8):
        allowed = lb.allow_request()
        print(f"  Request {i}: {'[ALLOWED]' if allowed else '[BLOCKED]'}")


def demo_leaky_bucket_queue():
    print("\n========================================")
    print("      LEAKY BUCKET (QUEUE) DEMO         ")
    print("========================================")

    def process_item(item):
        timestamp = time.strftime("%H:%M:%S")
        print(f"  [{timestamp}] Processed: {item}")

    # Queue Capacity = 3, Process Rate = 2 items/sec (0.5s interval)
    queue_shaper = LeakyBucketQueue(capacity=3, process_rate=2, processor_callback=process_item)
    queue_shaper.start()

    print("--> Enqueueing 5 items rapidly into queue of size 3:")
    for i in range(1, 6):
        success = queue_shaper.enqueue(f"Job #{i}")
        status = "Enqueued" if success else "Dropped (Queue Full)"
        print(f"  Push Job #{i}: {status}")

    print("\n--> Waiting for queue processor to drain items...")
    time.sleep(2.5)
    queue_shaper.stop()


if __name__ == "__main__":
    demo_token_bucket()
    demo_leaky_bucket_meter()
    demo_leaky_bucket_queue()