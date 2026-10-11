# Thread-Safe Queue

A generic thread-safe FIFO queue implemented in Python using `deque` and `threading.Condition`.

## Features

- Thread-safe `put()` and blocking `get()` operations.
- Producer-consumer pattern.
- Pytest tests with setup and teardown methods, parameterization, and fixtures.

## Run

```bash
python thread_safe_queue.py
```

## Run Tests

```bash
pip install pytest
pytest -v
```