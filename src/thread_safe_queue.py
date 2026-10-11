from collections import deque
from threading import Condition, Thread
from typing import Generic, TypeVar

T = TypeVar("T")


class ThreadSafeQueue(Generic[T]):
    def __init__(self) -> None:
        self._items: deque[T] = deque()
        self._condition = Condition()

    def put(self, item: T) -> None:
        with self._condition:
            self._items.append(item)
            self._condition.notify()

    def get(self) -> T:
        with self._condition:
            while not self._items:
                self._condition.wait()

            return self._items.popleft()


if __name__ == "__main__":
    q = ThreadSafeQueue[int]()

    def producer(q: ThreadSafeQueue[int]) -> None:
        for i in range(5):
            q.put(i)
            print(f"Produced: {i}")

    def consumer(q: ThreadSafeQueue[int]) -> None:
        for _ in range(5):
            item = q.get()
            print(f"Consumed: {item}")

    p = Thread(target=producer, args=(q,))
    c = Thread(target=consumer, args=(q,))

    p.start()
    c.start()

    p.join()
    c.join()
