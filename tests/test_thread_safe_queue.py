import threading

import pytest

from src.thread_safe_queue import ThreadSafeQueue


class TestThreadSafeQueue:
    def setup_method(self):
        self.q = ThreadSafeQueue[int]()
        self.threads = []

    def teardown_method(self):
        # Release consumers that may still be blocked on get().
        for thread in self.threads:
            if thread.is_alive():
                self.q.put(-1)

        for thread in self.threads:
            thread.join(timeout=2)

    def test_put_and_get(self):
        self.q.put(10)

        assert self.q.get() == 10

    @pytest.mark.parametrize(
        "items",
        [
            [1, 2, 3],
            [5, 4, 3, 2, 1],
            [10, 20, 30],
        ],
    )
    def test_fifo_order(self, items):
        for item in items:
            self.q.put(item)

        result = [self.q.get() for _ in items]

        assert result == items

    def test_get_blocks_until_item_is_available(self):
        started = threading.Event()
        result = []

        def consume_one():
            started.set()
            result.append(self.q.get())

        thread = threading.Thread(target=consume_one)
        self.threads.append(thread)
        thread.start()

        started.wait(timeout=2)
        self.q.put(42)
        thread.join(timeout=2)

        assert result == [42]

    def test_consumer_thread_terminates_after_put(self):
        started = threading.Event()

        def consume_one():
            started.set()
            self.q.get()

        thread = threading.Thread(target=consume_one)
        self.threads.append(thread)
        thread.start()

        started.wait(timeout=2)
        self.q.put(99)
        thread.join(timeout=2)

        assert not thread.is_alive()

    def test_producer_adds_five_items(self, capsys):
        def producer(q: ThreadSafeQueue[int]) -> None:
            for i in range(5):
                q.put(i)
                print(f"Produced: {i}")

        producer(self.q)

        output = capsys.readouterr().out
        produced = [
            line for line in output.splitlines() if line.startswith("Produced:")
        ]

        assert len(produced) == 5

    def test_consumer_consumes_five_items(self, capsys):
        def consumer(q: ThreadSafeQueue[int]) -> None:
            for _ in range(5):
                item = q.get()
                print(f"Consumed: {item}")

        for i in range(5):
            self.q.put(i)

        consumer(self.q)

        output = capsys.readouterr().out
        consumed = [
            line for line in output.splitlines() if line.startswith("Consumed:")
        ]

        assert len(consumed) == 5

    def test_concurrent_producers_and_consumers(self):
        produced_items = list(range(100))
        consumed_items = []
        lock = threading.Lock()

        def produce():
            for item in produced_items:
                self.q.put(item)

        def consume():
            for _ in produced_items:
                item = self.q.get()
                with lock:
                    consumed_items.append(item)

        producer_thread = threading.Thread(target=produce)
        consumer_thread = threading.Thread(target=consume)

        self.threads.extend([producer_thread, consumer_thread])

        consumer_thread.start()
        producer_thread.start()

        producer_thread.join(timeout=5)
        consumer_thread.join(timeout=5)

        assert sorted(consumed_items) == produced_items


@pytest.fixture
def sample_items():
    return [1, 2, 3, 4, 5]


def test_queue_with_fixture(sample_items):
    q = ThreadSafeQueue[int]()

    for item in sample_items:
        q.put(item)

    assert [q.get() for _ in sample_items] == sample_items
