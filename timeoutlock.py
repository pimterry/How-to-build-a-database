from threading import RLock

class TimeoutLock:
    """
    A context manager lock, with a timeout. Works as normal within the timeout,
    throws a TimeoutException if no lock is obtained within the timeout
    """

    def __init__(self, timeout):
        self.lock = RLock()
        self.timeout = timeout

    def __enter__(self):
        locked = self.lock.acquire(timeout=self.timeout)
        if not locked:
            raise TimeoutError()

    def __exit__(self, type, value, traceback):
        self.lock.release()

exports = TimeoutLock