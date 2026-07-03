A mutex (short for "mutual exclusion") is a synchronization primitive that ensures only one thread or process can access a shared resource at a time.

It works like a lock: before touching shared data, a thread must **acquire** the mutex. If another thread already holds it, the requester blocks (waits) until the holder **releases** it. This prevents race conditions — bugs where concurrent reads and writes to the same data interleave unpredictably and corrupt state.

Key characteristics:

- **Ownership** — the thread that locks the mutex is the one that must unlock it (unlike a semaphore, which any thread can signal).
- **Binary** — it's either locked or unlocked; there's no counting.
- **Critical section** — the code between acquire and release is the protected region, and you generally want to keep it as short as possible.

The main pitfalls are **deadlock** (two threads each waiting on a mutex the other holds) and forgetting to release, which is why most languages offer scoped helpers like `std::lock_guard` in C++, `with lock:` in Python, or `Mutex<T>` in Rust that release automatically.
