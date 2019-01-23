import queue
import threading
import time 


class FileToWrite:
    def __init__(self, path, file):
        self.path = path
        self.content = file

class AsyncWriter:
    def __init__(self):
        self.queue = queue.Queue(1000)
        self.open = True
        self.worker = threading.Thread(target=self.worker)
        self.worker.start()

    def write(self, path: str, file):
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
        item.file.save(item.path)

