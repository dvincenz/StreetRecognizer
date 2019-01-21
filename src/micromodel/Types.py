class DataPoint:
    def __init__(self, measurements: [(int, int, int)], response: int):
        self.measurements = measurements
        self.response = response
