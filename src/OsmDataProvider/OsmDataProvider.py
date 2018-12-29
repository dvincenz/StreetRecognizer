import overpass
import json
import geojson
from osgeo import gdal,ogr,osr


class OsmDataProvider:
    def __init__(self):
        self.api = overpass.API()

    def get_ways_by_coordinates(self, outputFile: str, lower_left: [], upper_right: []):
        response = self.api.get('(way["highway"] ('+ str(lower_left[1]) + ', ' + str(lower_left[0]) + ', ' + str(upper_right[1]) + ', ' + str(upper_right[0]) + '); >; ); out geom;')
        self._write_geojson(self._get_ways(response), outputFile)

    def get_ways_by_image(self, outputFile: str, image_path: str):
        ds = gdal.Open(image_path)
        gt = ds.GetGeoTransform()
        coordinates = self._get_corner_coordinates(gt, ds.RasterXSize, ds.RasterYSize)
        self.get_ways_by_coordinates(outputFile, coordinates[1], coordinates[2])

    
    def _get_ways(self, response: geojson.feature.FeatureCollection):
        features = response["features"]
        ways = []
        for feature in features:
            if feature["geometry"]["type"] == "LineString":
                ways.append(feature)
        return ways

    def _write_geojson(self, data, outputFile: str):
        f = open(outputFile, 'w' )
        f.write(json.dumps(data))
        f.close()

    def _get_corner_coordinates(self, transformation: [], cols: int, rows: int):
        upper_left = [transformation[0], transformation[3]]
        lower_left = [transformation[0],transformation[3] + (transformation[5]*rows)]
        upper_right = [transformation[0] + (transformation[1]*cols), transformation[3]]
        lower_right = [transformation[0] + (transformation[1]*cols), transformation[3] + (transformation[5]*rows)]
        return [upper_left, lower_left, upper_right, lower_right]



# response = api.get('(way ["highway"] (46.7766071, 9.0754762, 46.8044239, 9.1335982); >; ); out geom;')

# 