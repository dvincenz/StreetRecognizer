import os
import geojson
import json
from geoutils.Types import GeoLines

path = '../data/in/osm/training-data-micro-fine_gravel.json'
with open(file=path, mode='r', encoding='UTF-8') as file:
    json = geojson.load(file)


line_strings = []
for way in json.features:
    if isinstance(way.geometry, geojson.LineString):
        line_strings.append(way)


geolines = GeoLines(line_strings)

p = geolines.random_points(10000)

p[1].north