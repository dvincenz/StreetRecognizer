
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
        if not self.filter.values.get("unclassified"):
            self.filter.values["unclassified"] = 1
        if not self.filter.values.get("default"):
            self.filter.values["default"] = 1


    @staticmethod
    def _get_filter():
        filter = {}
        filter["primary"] = 180
        filter["primary_link"] = 180
        filter["motorway"] = 170
        filter["motorway_link"] = 170
        filter["trunk"] = 160
        filter["trunk_link"] = 160
        filter["secondary"] = 150
        filter["secondary_link"] = 150
        filter["tertiary"] = 140
        filter["tertiary_link"] = 140
        filter["residential"] = 130
        filter["living_street"] = 120
        filter["track"] = 110
        filter["construction"] = 100
        filter["service"] = 90
        filter["cycleway"] = 80
        filter["footway"] = 70
        filter["steps"] = 60
        filter["footway"] = 50
        filter["path"] = 40
        filter["pedestrian"] = 30
        filter["footway"] = 20
        filter["path"] = 10
        return ImageProcessorFilter("burn", "highway", filter)

