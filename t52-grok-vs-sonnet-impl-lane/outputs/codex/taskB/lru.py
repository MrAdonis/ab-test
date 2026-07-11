class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")

        self.capacity = capacity
        self.cache = {}

        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key) -> int:
        node = self.cache.get(key)
        if node is None:
            return -1

        self._move_to_front(node)
        return node.value

    def put(self, key, value) -> None:
        node = self.cache.get(key)

        if node is not None:
            node.value = value
            self._move_to_front(node)
            return

        if len(self.cache) >= self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]

        node = _Node(key, value)
        self.cache[key] = node
        self._add_to_front(node)

    def _move_to_front(self, node) -> None:
        self._remove(node)
        self._add_to_front(node)

    def _add_to_front(self, node) -> None:
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove(self, node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev


class _Node:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
