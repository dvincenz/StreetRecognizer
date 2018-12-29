import overpass
import json
import os
import geojson
from osgeo import gdal
from shapely.geometry import LineString, mapping
from OsmDataProviderConfig import OsmDataProviderConfig

from descartes import PolygonPatch
import matplotlib.pyplot as plot

class OsmDataProvider:
    def __init__(self, config: OsmDataProviderConfig):
        self.config = config
        self.api = overpass.API()

    def export_ways_by_coordinates(self, lower_left: [], upper_right: [],  output_file: str = ""):
        if output_file == "":
            output_file = self.config.default_output_file_name
        response = self.api.get('(way["highway"] ('+ str(lower_left[1]) + ', ' + str(lower_left[0]) + ', ' + str(upper_right[1]) + ', ' + str(upper_right[0]) + '); >; ); out geom;')
        ways_as_line = self._get_ways(response)
        self._write_geojson(ways_as_line, self.config.output_path + "/" + output_file + "_line.json")
        ways_as_polygon = self._tranform_ways_to_polygons(ways_as_line)
        self._write_geojson(ways_as_polygon, self.config.output_path + "/" + output_file + "_polygon.json")

    def export_ways_by_image(self, image_path: str):
        ds = gdal.Open(image_path)
        output_file_name = os.path.basename(image_path)[:-4]
        gt = ds.GetGeoTransform()
        coordinates = self._get_corner_coordinates(gt, ds.RasterXSize, ds.RasterYSize)
        self.export_ways_by_coordinates(coordinates[1], coordinates[2], output_file_name)

    
    def _get_ways(self, response: geojson.feature.FeatureCollection):
        features = response["features"]
        ways = []
        for feature in features:
            if feature["geometry"]["type"] == "LineString":
                ways.append(feature)
        return ways

    def _write_geojson(self, ways, output_file: str):
        if not os.path.exists(self.config.output_path):
            os.makedirs(self.config.output_path)
        data = {}
        data["features"] = ways
        data["type"] = "FeatureCollection"
        with open(output_file, 'w') as f:
            f.write(json.dumps(data))
        print("exported " + output_file)

    def _get_corner_coordinates(self, transformation: [], cols: int, rows: int):
        upper_left = [transformation[0], transformation[3]]
        lower_left = [transformation[0],transformation[3] + (transformation[5]*rows)]
        upper_right = [transformation[0] + (transformation[1]*cols), transformation[3]]
        lower_right = [transformation[0] + (transformation[1]*cols), transformation[3] + (transformation[5]*rows)]
        return [upper_left, lower_left, upper_right, lower_right]

    def _tranform_ways_to_polygons(self, lines):
        for way in lines:
            line = LineString(way["geometry"]["coordinates"])
            way["geometry"] = mapping(line.buffer(self._get_buffer(way)))
        return lines

    def _get_buffer(self, way):
        try:
            return self.config.buffer[way["properties"]["highway"]]
        except:
            return self.config.buffer["default"]


## troubleshooting methods
    def _print_polygons(self, polygons):
        BLUE = '#6699cc'
        fig = plot.figure() 
        ax = fig.gca() 
        for poly in polygons:
            ax.add_patch(PolygonPatch(poly, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2))
        ax.axis('scaled')
        plot.savefig('../data/temp/test.png', dpi=300)
