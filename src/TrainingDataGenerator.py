### This file generates the training and test data set used with our micro model.
### Inspired by CIFAR-10, this generates 60k 32x32 pixel images labeled across
### 10 classes. There are 6k images per class.

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
import random
import sqlite3

import geojson
from PIL import Image

from geodataprovider.GeoDataProvider import GeoDataProvider
from geoutils.Types import GeoPoint, GeoLines
from osmdataprovider.OsmDataProvider import OsmDataProvider
from osmdataprovider.OsmDataProviderConfig import OsmDataProviderConfig

# According to http://taginfo.openstreetmap.ch/keys/surface#values, the 10 most
# labeled surfaces are: asphalt, gravel, paved, ground, unpaved, grass, dirt, concrete, compacted, fine_gravel
# fine_gravel has 2'424 labeled highways, therefor taking 3 random samples from every highway suffices to
# obtain 6k images in total for every class.


CLASSES = [
    'asphalt',
    'gravel',
    'paved',
    'ground',
    'unpaved',
    'grass',
    'dirt',
    'concrete',
    'compacted',
    'fine_gravel'
]

def _parse_args():
    parser = argparse.ArgumentParser(description='Generates training (and test) data for the micro model.')
    parser.add_argument('-o', '--output', type=str, default='../data/in/micro', help='directory path to place the generated training images')
    parser.add_argument('--meta-data', type=str, default='../data/metadata.db', help='path to the metadata sqlite database file')
    parser.add_argument('--osm-path', type=str, default='../data/in/osm', help='directory path to read/write OSM data to/from')
    parser.add_argument('--num-threads', type=int, help='maximum number of threads to run concurrently (default: unlimited)')
    parser.add_argument('-p', '--pbf', type=str, help='OSM PBF extract used as input, obtained from e.g. https://planet.osm.ch/')
    parser.add_argument('--sample-size', type=int, default=32, help='size in pixels of the sample images taken at each point (default: 32)')
    parser.add_argument('--sample-number', type=int, default=2000, help='number of random images per category (default 2000)')
    return vars(parser.parse_args())

def _export_labeled_ways(provider: OsmDataProvider, num_threads: int = len(CLASSES)):
    def _run(surface: str):
        print("[Thread-{0}] Starting...".format(surface))
        provider.export_ways_by_surface_from_pbf(
            surface=surface,
            output_file="training-data-micro-{0}.json".format(surface))
        print("[Thread-{0}] Exiting...".format(surface))

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for future in executor.map(_run, CLASSES):
            future.result()

    print("Done!")

def _find_ortho_photo(cursor: sqlite3.Cursor, point: GeoPoint) -> str:
    result = cursor.execute('''
        SELECT file_path FROM orthos
        WHERE east_min < ?
        AND east_max > ?
        AND north_min < ?
        AND north_max > ?
    ''', (point.east, point.east, point.north, point.north)).fetchone()

    if result is None:
        return None

    print('Point {0} => Ortho {1}'.format(point, result[0]))
    return result[0]


def _get_sample_image(point: GeoPoint, size: int, cursor: sqlite3.Cursor) -> Image:
    geo_tiff_path = _find_ortho_photo(cursor=cursor, point=point)
    if geo_tiff_path is None:
        raise ValueError('Could not find an Orthophoto for {0}'.format(point))

    geodataprovider = GeoDataProvider(geo_tiff_path=geo_tiff_path)
    x, y = geodataprovider.geo_point_to_pixel(point)
    image = Image.open(geo_tiff_path)

    if not 0 <= x <= image.size[0] or not 0 <= y <= image.size[1]:
        raise ValueError('GeoPoint {0} is outside Orthophoto {1}'.format(point, geo_tiff_path))

    return image.crop((x - size / 2, y - size / 2, x + size / 2, y + size / 2))

def run():
    args = _parse_args()

# Set a fixed seed for reproducible debugging
    random.seed(2)

# 0) Export all labeled ways to geojson
    if args['pbf']:
        print("Reading labeled ways from Switzerland extract, this might take several minutes...")
        _export_labeled_ways(
            provider=OsmDataProvider(config=OsmDataProviderConfig(
                pbf_path=args['pbf'],
                output_path=args['osm_path'])),
            num_threads=args['num_threads'])
    else:
        print("--pbf not provided; skipping OSM export")

# 1) Randomly select 2'000 ways among all labeled ways in Switzerland
    print('Selecting sample ways among all labeled ways...')

    ways = {}
    for surface in CLASSES:
        with open(
                file=os.path.join(
                    args['osm_path'],
                    'training-data-micro-{0}.json'.format(surface)),
                mode='r',
                encoding='UTF-8') as file:
            json = geojson.load(file)

        ways[surface] = {}
        
        line_strings = []
        for way in json.features:
            if isinstance(way.geometry, geojson.LineString):
                line_strings.append(way)

        ways[surface]['ways'] = line_strings
        geo_lines = GeoLines(line_strings)
        ways[surface]['points'] = geo_lines.random_points(args['sample_number'])

# # 2) Pick 3 points along every way
#     print('Picking sample points along selected ways...')

#     for surface in CLASSES:
#         ways[surface]['points'] = []
#         for way in ways[surface]['ways']:
#             # TODO: Select more than one point per way
#             coords = way.geometry.coordinates
#             ways[surface]['points'].append(coords[min(3, len(coords)-1)])

# 3) Take a sample image at the selected points
    print('Taking sample image for every selected point...')

    Image.MAX_IMAGE_PIXELS = 20000 * 20000

    conn = sqlite3.connect(args['meta_data'])
    cursor = conn.cursor()

    for surface in CLASSES:
        ways[surface]['samples'] = []
        for point in ways[surface]['points']:
            try:
                sample = _get_sample_image(
                    point=GeoPoint(east=point.north, north=point.east),
                    size=args['sample_size'],
                    cursor=cursor)
                ways[surface]['samples'].append(sample)
            except ValueError as ex:
                print('Could not create sample image for surface {0}:\n\t{1}'.format(surface, ex))

    conn.commit()
    conn.close()

# 4) Store the images in labeled directories
    print('Storing sample images in output directory ({0})...'.format(args['output']))

    for surface in CLASSES:
        os.makedirs(os.path.join(args['output'], surface), exist_ok=True)
        for i, sample in enumerate(ways[surface]['samples']):
            sample.save(os.path.join(args['output'], surface, '{0:04d}.png'.format(i)), 'PNG')

if __name__ == "__main__":
    run()
