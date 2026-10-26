"""
test_rate_limiters.py
Automated tests for rate limiting algorithms.
"""

import unittest
import time
from rate_limiters import TokenBucket, LeakyBucketMeter, LeakyBucketQueue


class TestTokenBucket(unittest.TestCase):
    def test_burst_and_refill(self):
        tb = TokenBucket(capacity=2, refill_rate=1)
        self.assertTrue(tb.allow_request())
        self.assertTrue(tb.allow_request())
        self.assertFalse(tb.allow_request())  # Capacity exhausted

        time.sleep(1.1)  # Refill 1 token
        self.assertTrue(tb.allow_request())
        self.assertFalse(tb.allow_request())


class TestLeakyBucketMeter(unittest.TestCase):
    def test_capacity_and_leak(self):
        lb = LeakyBucketMeter(capacity=2, leak_rate=1)
        self.assertTrue(lb.allow_request())
        self.assertTrue(lb.allow_request())
        self.assertFalse(lb.allow_request())  # Bucket full

        time.sleep(1.1)  # Leak 1 unit
        self.assertTrue(lb.allow_request())
        self.assertFalse(lb.allow_request())


class TestLeakyBucketQueue(unittest.TestCase):
    def test_queue_overflow(self):
        processed = []
        shaper = LeakyBucketQueue(capacity=2, process_rate=10, processor_callback=processed.append)
        
        self.assertTrue(shaper.enqueue("A"))
        self.assertTrue(shaper.enqueue("B"))
        self.assertFalse(shaper.enqueue("C"))  # Overflow


if __name__ == "__main__":
    unittest.main()