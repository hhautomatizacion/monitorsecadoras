import time
import collections

class ReadingBuffer:
    def __init__(self, db, max_size=10000):
        self.db = db
        self.queue = collections.deque()
        self.max_size = max_size
        self.last_try = 0

    def used_pct(self):
        return int(len(self.queue) * 100 / self.max_size)
    
    def add(self, reading):
        if len(self.queue) >= self.max_size:
            self.queue.popleft()
        self.queue.append(reading)

    def flush(self):
        if not self.queue:
            return
        if time.time() - self.last_try < 60:
            return
        self.last_try = time.time()
        if not self.db.ensure_alive():
            return
        while self.queue:
            reading = self.queue[0]
            try:
                self.db.insert_reading(reading)
                self.queue.popleft()
            except Exception as e:
                print("[DB] error insertando, se reintentará:", e)
                break
