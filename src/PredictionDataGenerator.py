import argparse
from concurrent.futures import ThreadPoolExecutor
import os
import re

import geojson
import numpy
import progressbar
import sqlite3

from geoutils.RandomImageProvider import RandomImageProvider
from geoutils.Types import GeoPoint, GeoRect
from osmdataprovider import Provider
from osmdataprovider.OsmDataProviderConfig import OsmDataProviderConfig

def _parse_args():
    parser = argparse.ArgumentParser(description='Generates prediction data for the micro model.')
    parser.add_argument('-o', '--output', type=str, default='../data/in/micro-predict', help='directory path to place the generated prediction images')
    parser.add_argument('--meta-data', type=str, default='../data/metadata.db', help='path to the metadata sqlite database file')
    parser.add_argument('--osm-path', type=str, default='../data/in/osm', help='directory path to read/write OSM data to/from')
    parser.add_argument('-n', '--number', type=int, help='maximum number of streets to generate prediction data for (default: unlimited)')
    parser.add_argument('--num-threads', type=int, help='maximum number of threads to run concurrently (default: unlimited)')
    parser.add_argument('-p', '--pbf', type=str, help='OSM PBF extract used as input, obtained from e.g. https://planet.osm.ch/')
    parser.add_argument('--partitions', type=int, default=5, help='number of partitions to split the osm extract into per dimension (default: 2)')
    parser.add_argument('--sample-size', type=int, default=32, help='size in pixels of the sample images taken at each point (default: 32)')
    parser.add_argument('--sample-number', type=int, default=3, help='number of samples per way (default 3)')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose output')
    return vars(parser.parse_args())

def run():
    args = _parse_args()

# 0) Export all unlabeled ways to geojson, this needs to be done in sections, since osmtogeojson crashes on too large data sets
    if args['pbf']:
        osm_data_provider = Provider(config=OsmDataProviderConfig(
            output_path=args['osm_path'],
            pbf_path=args['pbf']
        ))

        def _run(arg: (int, GeoPoint)):
            osm_data_provider.export_unlabeled_ways_in_area_from_pbf(
                bbox=arg[1],
                output_file='unlabeled-ways-{0:02d}.json'.format(arg[0])
            )

        partitions = _get_partitions(args['meta_data'], args['partitions'])
        num_threads = len(partitions)
        if args['num_threads']:
            num_threads = min(args['num_threads'], num_threads)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for future in executor.map(_run, enumerate(partitions)):
                future.result()

        print('pbf export finished')
    else:
        print("--pbf not provided; skipping OSM export")

# 1) Create sample images of all ways (or subset thereof)
    for file in os.listdir(args['osm_path']):
        if re.fullmatch(r'unlabeled-ways-\d+\.json', file):
            _create_prediction_samples(
                geojson_file=os.path.join(args['osm_path'], file),
                meta_data=args['meta_data'],
                number=args['number'],
                output=args['output'],
                sample_number=args['sample_number'],
                sample_size=args['sample_size'],
                verbose=args['verbose']
            )

def _get_partitions(metadata, partitions):
    conn = sqlite3.connect(metadata)
    cursor = conn.cursor()

    limits = cursor.execute('''
        SELECT MIN(east_min), MIN(north_min), MAX(east_max), MAX(north_max)
        FROM orthos
    ''').fetchone()

    if limits is None:
        raise ValueError('Could not determine partitions, please check your database!')

    conn.commit()
    conn.close()

    result = []
    east_step = (limits[2] - limits[0]) / partitions
    north_step = (limits[3] - limits[1]) / partitions
    for east in numpy.linspace(limits[0], limits[2], partitions, endpoint=False):
        for north in numpy.linspace(limits[1], limits[3], partitions, endpoint=False):
            result.append(GeoRect(
                a=GeoPoint(east=east+east_step, north=north+north_step),
                b=GeoPoint(east=east, north=north)
            ))

    return result

def _create_prediction_samples(geojson_file, meta_data, number, output, sample_size, sample_number, verbose):
    print('Creating prediction samples for {0}'.format(geojson_file))
    with open(geojson_file, mode='r', encoding='UTF-8') as file:
        geojson_data = geojson.load(file)

    line_strings = []
    for way in geojson_data.features:
        if isinstance(way.geometry, geojson.LineString):
            line_strings.append(way)

    widgets = [
        ' [', os.path.basename(os.path.normpath(output)), '] ',
        progressbar.Percentage(), ' ',
        progressbar.SimpleProgress(), ' ',
        progressbar.Bar(),
        progressbar.Timer(), ' ',
        progressbar.ETA()
    ]

    maximum_lines = len(line_strings)

    if number:
        maximum_lines = min(number, maximum_lines)

    with progressbar.ProgressBar(max_value=maximum_lines, widgets=widgets) as bar:
        # TODO: This loop is slow AF, since we always only pass 1 street to the RandomImageProvider,
        # which makes it impossible to optimize loading of the Orthos across streets. To optimize this,
        # it would require a decently large re-write of the RandomImageProvider.
        for i in range(0, maximum_lines):
            line_string = line_strings[i] # TODO: This can cause duplicated streets across partitions
            with RandomImageProvider(
                    image_size=sample_size,
                    out_path=os.path.join(output, line_string.id[4:]),
                    metadata=meta_data,
                    verbose=verbose
            ) as rip:
                rip.get_random_images(
                    number=sample_number,
                    line_strings=[line_string],
                    show_progress=verbose
                )
            bar.update(i+1)

if __name__ == "__main__":
    run()
