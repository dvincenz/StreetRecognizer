import os
import queue
import threading

from PIL import Image

class FileToWrite:
    def __init__(self, path, file: Image):
        self.path = path
        self.file = file

class AsyncWriter:
    def __init__(self):
        self.queue = queue.Queue(1000)
        self.open = True
        self._worker = threading.Thread(target=self.worker)
        self._worker.start()

    def write(self, file, path: str,):
        self.queue.put(FileToWrite(path, file))

    def worker(self):
        while True:
            item = self.queue.get()
            if item is None:
                break
            self.write_file(item)
            self.queue.task_done()

    def close(self):
        self.queue.put(None)
        self._worker.join()

    def write_file(self, item: FileToWrite):
        os.makedirs(os.path.dirname(item.path), exist_ok=True)
        item.file.save(item.path, 'PNG')
