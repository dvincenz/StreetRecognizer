class OsmDataProviderConfig:
    def __init__(self, output_path: str, buffer: list, default_output_file_name: str = "output"):
        self.output_path = output_path
        self.default_output_file_name = default_output_file_name
        self.buffer = buffer
        self.buffer["default"] = 0.000025