Write a Python module `lru.py` implementing an LRU (least-recently-used) cache:

    class LRUCache:
        def __init__(self, capacity: int): ...
        def get(self, key) -> int: ...      # returns the value, or -1 if key not present
        def put(self, key, value) -> None: ...

Behavior:
- `capacity` is a positive integer — the maximum number of key/value pairs the cache holds.
- Both `get` and `put` count as "using" a key (they make it the most-recently-used).
- When a `put` would exceed capacity, evict the least-recently-used key before inserting.
- `put` on an existing key updates its value (and does not grow the size).
- `get` on a missing key returns `-1`.

Both `get` and `put` must run in average O(1) time.

Only output the contents of `lru.py`. No tests, no explanation.
