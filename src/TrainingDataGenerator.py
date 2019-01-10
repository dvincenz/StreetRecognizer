### This file generates the training and test data set used with our micro model.
### Inspired by CIFAR-10, this generates 60k 32x32 pixel images labeled across
### 10 classes. There are 6k images per class.

import argparse
from concurrent.futures import ThreadPoolExecutor
import os

import geojson
from PIL import Image

from geodataprovider.GeoDataProvider import GeoDataProvider
from geoutils.Types import GeoPoint
import imageprovider
from imageprovider.ImageProviderConfig import ImageProviderConfig
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
    parser.add_argument('--ortho-input', type=str, default='../data/in/ortho/raw', help='directory path to read/write LV95 orthophotos to/from')
    parser.add_argument('--ortho-output', type=str, default='../data/in/ortho/wgs84', help='directory path to read/write WGS84 orthophotos to/from')
    parser.add_argument('--osm-path', type=str, default='../data/in/osm', help='directory path to read/write OSM data to/from')
    parser.add_argument('--num-threads', type=int, help='maximum number of threads to run concurrently (default: unlimited)')
    parser.add_argument('-p', '--pbf', type=str, help='OSM PBF extract used as input, obtained from e.g. https://planet.osm.ch/')
    parser.add_argument('--sample-size', type=int, default=32, help='size in pixels of the sample images taken at each point (default: 32)')
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

def _find_ortho_photo(point: GeoPoint) -> str:
    photos = {
        GeoPoint(east=7.6014623, north=46.7419138): '1207-23',
        GeoPoint(east=9.0017667, north=46.0051708): '1353-22',
        GeoPoint(east=7.5595237, north=46.4930792): '1247-32',
        GeoPoint(east=8.6049809, north=47.3848953): '1091-24',
        GeoPoint(east=8.9361872, north=47.3577915): '1093-32',
        GeoPoint(east=8.9373588, north=47.3634548): '1093-32',
        GeoPoint(east=8.5119648, north=47.4093956): '1091-12',
        GeoPoint(east=7.6233479, north=46.7494293): '1207-23',
        GeoPoint(east=8.6994310, north=47.4774382): '1072-32',
        GeoPoint(east=8.7135327, north=47.5119557): '1072-12'
    }
    return photos.get(point)

def _get_sample_image(point: GeoPoint, size: int, input_path: str, output_path: str) -> Image:
    geo_tiff_number = _find_ortho_photo(point)
    if geo_tiff_number is None:
        raise ValueError('Could not find an Orthophoto for {0}'.format(point))

    image_provider = imageprovider.Provider(config=ImageProviderConfig(
        azure_blob_account='swisstopo',
        input_path=input_path,
        output_path=output_path))
    images = image_provider.get_image_as_wgs84(geo_tiff_number)
    geo_tiff_path = os.path.join(output_path, images[0])

    geodataprovider = GeoDataProvider(geo_tiff_path=geo_tiff_path)
    x, y = geodataprovider.geo_point_to_pixel(point)
    image = Image.open(geo_tiff_path)

    if not 0 <= x <= image.size[0] or not 0 <= y <= image.size[1]:
        raise ValueError('GeoPoint {0} is outside Orthophoto {1}'.format(point, geo_tiff_path))

    return image.crop((x - size / 2, y - size / 2, x + size / 2, y + size / 2))

def run():
    args = _parse_args()

# 0) Export all labeled ways to geojson
    if args['pbf']:
        print("Reading labeled ways from Switzerland extract, this might take several minutes...")
        _export_labeled_ways(
            provider=OsmDataProvider(config=OsmDataProviderConfig(
                pbf_path=args['pbf_input'],
                output_path=args['osm_path'])),
            num_threads=args['num_threads'])
    else:
        print("--pbf not provided; skipping OSM export")

# 1) Randomly select 2'000 ways among all labeled ways in Switzerland
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
        ways[surface]['ways'] = []
        for way in json.features:
            if isinstance(way.geometry, geojson.LineString):
                # TODO: Select more than simply the first one
                ways[surface]['ways'].append(way)
                break

# 2) Pick 3 points along every way
    for surface in CLASSES:
        ways[surface]['points'] = []
        for way in ways[surface]['ways']:
            # TODO: Select more than one point per way
            coords = way.geometry.coordinates
            ways[surface]['points'].append(coords[min(3, len(coords)-1)])

# 3) Take a sample image at the selected points
    Image.MAX_IMAGE_PIXELS = 20000 * 20000
    for surface in CLASSES:
        ways[surface]['samples'] = []
        for point in ways[surface]['points']:
            try:
                sample = _get_sample_image(
                    point=GeoPoint(east=point[0], north=point[1]),
                    size=args['sample_size'],
                    input_path=args['ortho_input'],
                    output_path=args['ortho_output'])
                ways[surface]['samples'].append(sample)
            except ValueError as ex:
                print('Could not create sample image for surface {0}:\n\t{1}'.format(surface, ex))

# 4) Store the images in labeled directories
    for surface in CLASSES:
        os.makedirs(os.path.join(args['output'], surface), exist_ok=True)
        for i, sample in enumerate(ways[surface]['samples']):
            sample.save(os.path.join(args['output'], surface, '{0:04d}.png'.format(i)), 'PNG')

if __name__ == "__main__":
    run()
