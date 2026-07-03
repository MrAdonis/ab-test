A mutex (short for "mutual exclusion") is a synchronization primitive that ensures only one thread can access a shared resource at a time. A thread must acquire (lock) the mutex before entering a critical section of code, and release (unlock) it when done. If another thread tries to acquire an already-locked mutex, it blocks until the mutex is released.

This prevents race conditions — bugs where multiple threads read and write shared data simultaneously and produce inconsistent results. For example, two threads incrementing a shared counter can lose updates without a mutex protecting the increment.

Key points:
- **Ownership**: unlike a general semaphore, a mutex is typically owned by the thread that locked it, and only that thread should unlock it.
- **Trade-offs**: mutexes serialize access, which can create contention bottlenecks, and careless use can cause deadlocks (e.g., two threads each waiting for a lock the other holds).
