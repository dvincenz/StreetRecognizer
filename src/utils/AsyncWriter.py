import queue
import threading
import time 
import os

from PIL import Image




class FileToWrite:
    def __init__(self, path, file: Image):
        self.path = path
        self.file = file

class AsyncWriter:
    def __init__(self):
        self.queue = queue.Queue(1000)
        self.open = True
        self.worker = threading.Thread(target=self.worker)
        self.worker.start()

    def write(self, file,  path: str,):
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
        self.worker.join()

    def write_file(self, item: FileToWrite):
        if not os.path.exists(os.path.dirname(item.path)):
            os.makedirs(os.path.dirname(item.path))
        item.file.save(item.path, 'PNG')

