import geojson
from geoutils.Types import GeoLines

line_strings = []
with open(file='../data/in/osm/training-data-micro-fine_gravel.json',mode='r', encoding='UTF-8') as file:
    json = geojson.load(file) 
    for way in json.features:
        if isinstance(way.geometry, geojson.LineString):
            line_strings.append(way)


geolines = GeoLines(line_strings)

points = geolines.random_points(2000)
for point in points:
    print(point.east)


from utils.AsyncWriter import AsyncWriter

writer = AsyncWriter("fancy\path")
writer.write("fancy 1")
writer.write("fancy 2")
writer.write("fancy 3")
writer.write("fancy 4")
print("done")
writer.dispose()
writer.write("should be dead")
writer.write("holy fuck")
