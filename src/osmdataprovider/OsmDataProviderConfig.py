class OsmDataProviderConfig:
    def __init__(self,
            output_path: str,
            buffer=None,
            default_output_file_name: str = "output",
            pbf_path: str = None):

        self.output_path = output_path
        self.default_output_file_name = default_output_file_name
        self.pbf_path = pbf_path

        if not buffer:
            self.buffer = self._get_default_buffer()
        else: 
            self.buffer = buffer
        self.buffer["default"] = 0.000025

    @staticmethod
    def _get_default_buffer():
        default_buffer = {}
        default_buffer["unclassified"] = 0.000023
        default_buffer["tertiary"] = 0.000035
        default_buffer["tertiary_link"] = 0.000035
        default_buffer["footway"] = 0.000013
        default_buffer["path"] = 0.000013
        default_buffer["pedestrian"] = 0.000013
        default_buffer["track"] = 0.000020
        default_buffer["primary"] = 0.000045
        default_buffer["primary_link"] = 0.000045
        default_buffer["motorway_link"] = 0.000045
        default_buffer["motorway"] = 0.000045
        default_buffer["living_street"] = 0.000030
        default_buffer["cycleway"] = 0.000020
        default_buffer["footway"] = 0.000013
        default_buffer["construction"] = 0.000025
        default_buffer["residential"] = 0.000030
        default_buffer["steps"] = 0.000013
        default_buffer["secondary"] = 0.000040
        default_buffer["trunk"] = 0.000040
        default_buffer["trunk_link"] = 0.000040
        default_buffer["service"] = 0.000025
        return default_buffer
