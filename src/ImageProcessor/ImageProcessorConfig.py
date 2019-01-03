
class ImageProcessorFilter: 
    def __init__(self, name: str, field: str, values: [str, str]):
        self.field = field
        self.name = name
        self.values = values

class ImageProcessorConfig:
    def __init__(self, output_path: str, filter: ImageProcessorFilter = None):
        self.output_path = output_path
        if not filter:
            self.filter = self._get_filter()
        else:
            self.filter = filter
        if not self.filter.values.get("default"):
            self.filter.values["default"] = 1
        if not self.filter.values.get("empty"):
             self.filter.values["empty"] = 255

    @staticmethod
    def _get_filter():
        filter_values = {}
        filter_values["asphalt"] = 10
        filter_values["gravel"] = 20
        filter_values["ground"] = 30
        return ImageProcessorFilter("burn", "surface", filter_values)

