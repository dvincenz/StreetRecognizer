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
from utils.AsyncWriter import AsyncWriter
from geoutils.RandomImageProvider import RandomImageProvider

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
    parser.add_argument('--sample-number', type=int, default=6000, help='number of random images per category (default 6000)')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose output')
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





def run():
    args = _parse_args()

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

# 1) Randomly select points among all labeled ways in Switzerland
    print('Selecting sample ways among all labeled ways...')

    ways = {}
    def _random_images(surface: str):
        print('\tProcessing {0}...'.format(surface))
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
        with RandomImageProvider(
            image_size=args['sample_size'],
            out_path=os.path.join(args['output'], surface),
            metadata=args["meta_data"],
            verbose=args['verbose'],
            is_seed_fix=False
        ) as r:
            r.get_random_images(
                number=args["sample_number"], 
                line_strings=line_strings
            )
        return surface
    # because of to slow harddisc parallelizing this function on this machine makes no sence
    with ThreadPoolExecutor(max_workers=1) as executor:
        for future in executor.map(_random_images, CLASSES):
            print("done {0}".format(future))

    
if __name__ == "__main__":
    run()
