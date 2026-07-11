from lru import LRUCache


def test_basic_evict():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1
    c.put(3, 3)          # evicts key 2 (LRU)
    assert c.get(2) == -1
    c.put(4, 4)          # evicts key 1
    assert c.get(1) == -1
    assert c.get(3) == 3
    assert c.get(4) == 4


def test_get_counts_as_use():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    c.get(1)             # 1 becomes most-recently-used
    c.put(3, 3)          # so 2 should be evicted, not 1
    assert c.get(1) == 1
    assert c.get(2) == -1


def test_update_existing_no_grow():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    c.put(1, 10)         # update, size stays 2
    c.put(3, 3)          # evicts 2 (1 was just used)
    assert c.get(1) == 10
    assert c.get(2) == -1
    assert c.get(3) == 3


def test_capacity_one():
    c = LRUCache(1)
    c.put(1, 1)
    assert c.get(1) == 1
    c.put(2, 2)
    assert c.get(1) == -1
    assert c.get(2) == 2


def test_missing_returns_minus_one():
    c = LRUCache(2)
    assert c.get(99) == -1
