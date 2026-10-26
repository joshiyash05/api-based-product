# Python Rate Limiters

Thread-safe Token Bucket and Leaky Bucket algorithms written in pure Python.

## Files

- `rate_limiters.py`: Main module containing `TokenBucket`, `LeakyBucketMeter`, and `LeakyBucketQueue`.
- `demo.py`: Executable script demonstrating real-time rate limiting behavior.
- `test_rate_limiters.py`: Unit test suite.

## Execution

Run the demo script:
### Step 6: How to Run and Verify

Open your terminal in the `rate_limiter_project` directory and execute:

1. **Run the Demonstration:**
   ```bash
   python demo.py
   
2. **Run the Unit Test**
    ```bash
    python -m unittest test_rate_limiters.py