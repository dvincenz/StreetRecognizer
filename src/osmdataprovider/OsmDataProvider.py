import json
import os
from subprocess import call

from descartes import PolygonPatch
import geojson
import matplotlib.pyplot as plot
from osgeo import gdal
import overpass
from shapely.geometry import LineString, mapping

from descartes import PolygonPatch
from geodataprovider.GeoDataProvider import GeoDataProvider
from geoutils.Types import GeoRect
from osmdataprovider.OsmDataProviderConfig import OsmDataProviderConfig

class OsmDataProvider:
    def __init__(self, config: OsmDataProviderConfig):
        self.config = config
        self.not_defined_buffer = {}
        self.api = overpass.API()

    def get_ways_by_coordinates(self, lower_left: [], upper_right: []):
        if not self._validate_wgs84_coordinates(lower_left) or not self._validate_wgs84_coordinates(upper_right):
            raise ValueError('The coordinates of the image are not in range. Given coordinates ' + str(lower_left) + ', ' + str(upper_right))
        response = self.api.get('(way["highway"] ({0}, {1}, {2}, {3}); >; ); out geom;'.format(lower_left[1], lower_left[0], upper_right[1], upper_right[0]))
        return self._get_ways(response)

    def get_ways_by_id(self, id: int):
        response = self.api.get('(way({0}); >; ); out geom;'.format(id))
        return self._get_ways(response)


    def export_ways_by_coordinates(self, lower_left: [], upper_right: [], output_file: str = ""):
        if output_file == "":
            output_file = self.config.default_output_file_name
        ways_as_line = self.get_ways_by_coordinates(lower_left, upper_right)
        self._write_geojson(ways_as_line, self.config.output_path + "/" + output_file + "_line.json")
        ways_as_polygon = self._tranform_ways_to_polygons(ways_as_line)
        self._write_geojson(ways_as_polygon, self.config.output_path + "/" + output_file + "_polygon.json")

    def export_ways_by_image(self, image_path: str):
        ds = gdal.Open(image_path)
        output_file_name = os.path.basename(os.path.splitext(image_path)[0])
        gt = ds.GetGeoTransform()
        geo_data_provider = GeoDataProvider(image_path)
        self.export_ways_by_coordinates(geo_data_provider.get_lower_left_coordinates, geo_data_provider.get_upper_right_coordinates, output_file_name)

    def export_ways_by_surface_from_pbf(self, surface: str, output_file: str = ""):
        if output_file == "":
            output_file = self.config.default_output_file_name

        osm_xml_file = os.path.join(self.config.output_path, os.path.splitext(output_file)[0] + ".osm")
        osm_geojson_file = os.path.join(self.config.output_path, output_file)

        print("Reading ways with surface {0}...".format(surface))
        call([
            "osmosis",
            "--read-pbf", self.config.pbf_path,
            "--tf", "accept-ways", "surface={0}".format(surface),
            "--tf", "reject-relations",
            "--used-node",
            "--write-xml", osm_xml_file])
        with open(osm_geojson_file, 'w') as file:
                call(["osmtogeojson", osm_xml_file], stdout=file)

    def export_unlabeled_ways_in_area_from_pbf(self, bbox: GeoRect, output_file: str = ""):
        if output_file == "":
            output_file = self.config.default_output_file_name

        osm_xml_file = os.path.join(self.config.output_path, os.path.splitext(output_file)[0] + ".osm")
        osm_geojson_file = os.path.join(self.config.output_path, output_file)

        call([
            "osmosis",
            "--read-pbf", self.config.pbf_path,
            "--bounding-box", "top={0}".format(bbox.a.north), "left={0}".format(bbox.a.east), "bottom={0}".format(bbox.b.north), "right={0}".format(bbox.b.east),
            "--tf", "accept-ways", "highway=*",
            "--tf", "reject-ways", "surface=*",
            "--tf", "reject-relations",
            "--used-node",
            "--write-xml", osm_xml_file])
        with open(osm_geojson_file, 'w') as file:
                call(["node", "--max_old_space_size=10240", "/usr/local/bin/osmtogeojson", osm_xml_file], stdout=file)

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
            f.write(json.dumps(data, indent=4, sort_keys=True))
        print("exported " + output_file)

    def _tranform_ways_to_polygons(self, lines):
        for way in lines:
            line = LineString(way["geometry"]["coordinates"])
            way["geometry"] = mapping(line.buffer(self._get_buffer(way)))
        return lines

    def _get_buffer(self, way):
        highway = way["properties"]["highway"]
        try:
            return self.config.buffer[highway]
        except:
            if highway in self.not_defined_buffer:
                self.not_defined_buffer[highway] += 1 
            else:
                self.not_defined_buffer[highway] = 1
            return self.config.buffer["default"]

    def _validate_wgs84_coordinates(self, coordinates):
        return coordinates[0] < 90 and coordinates[0] > -90 and coordinates[1] < 180 and coordinates[1] > -180

## troubleshooting methods
    def _print_polygons(self, polygons):
        BLUE = '#6699cc'
        fig = plot.figure() 
        ax = fig.gca() 
        for poly in polygons:
            ax.add_patch(PolygonPatch(poly, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2))
        ax.axis('scaled')
        plot.savefig('../data/temp/test.png', dpi=300)
