import os
import random
import sqlite3

from PIL import Image

from geodataprovider.GeoDataProvider import GeoDataProvider
from geoutils.Types import GeoPoint, GeoLines
from osmdataprovider.OsmDataProvider import OsmDataProvider
from osmdataprovider.OsmDataProviderConfig import OsmDataProviderConfig
from utils.AsyncWriter import AsyncWriter

class RandomImageProvider:
    def __init__(self, image_size, out_path: str, metadata: str, verbose, is_seed_fix = False):
        self.image_size = image_size
        self.conn = sqlite3.connect(metadata)
        self.cursor = self.conn.cursor()
        self.out_path = out_path
        self.verbose = verbose
        self.writer = AsyncWriter()
        if is_seed_fix:
            random.seed(2)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()
        self.writer.close()

    def get_random_images(self, number: int, line_strings):
        geo_lines = GeoLines(line_strings)
        points = geo_lines.random_points(number)

        print('Taking sample image for every selected point...')
        Image.MAX_IMAGE_PIXELS = 20000 * 20000

        image_number = 0
        for point in points:
            try:
                sample = self._get_sample_image(point)
                self.writer.write(sample, os.path.join(self.out_path, '{0:04d}.png'.format(image_number)))
                image_number += 1
            except ValueError as ex:
                print('Could not create sample image:\n\t{0}'.format(ex))
    

    def _find_ortho_photo(self, point: GeoPoint) -> str:
        result = self.cursor.execute('''
            SELECT file_path FROM orthos
            WHERE east_min < ?
            AND east_max > ?
            AND north_min < ?
            AND north_max > ?
        ''', (point.east, point.east, point.north, point.north)).fetchone()

        if result is None:
            return None

        if self.verbose:
            print('Point {0} => Ortho {1}'.format(point, result[0]))

        return result[0]

    def _get_sample_image(self, point: GeoPoint) -> Image:
        geo_tiff_path = self._find_ortho_photo(point)
        if geo_tiff_path is None:
            raise ValueError('Could not find an Orthophoto for {0}'.format(point))

        geodataprovider = GeoDataProvider(geo_tiff_path=geo_tiff_path)
        x, y = geodataprovider.geo_point_to_pixel(point)
        image = Image.open(geo_tiff_path)

        if not 0 <= x <= image.size[0] or not 0 <= y <= image.size[1]:
            raise ValueError('GeoPoint {0} is outside Orthophoto {1}'.format(point, geo_tiff_path))

        return image.crop((x - self.image_size / 2, y - self.image_size / 2, x + self.image_size / 2, y + self.image_size / 2))

