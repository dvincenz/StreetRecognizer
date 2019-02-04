import os
import random
import sqlite3
import progressbar

from PIL import Image

from geodataprovider.GeoDataProvider import GeoDataProvider
from geoutils.Types import GeoPoint, GeoLines
from utils.AsyncWriter import AsyncWriter

class RandomImageProvider:
    def __init__(self, image_size, out_path: str, metadata: str, verbose, is_seed_fix=False):
        self.image_size = image_size
        self.conn = sqlite3.connect(metadata)
        self.cursor = self.conn.cursor()
        self.out_path = out_path
        self.verbose = verbose
        self.writer = AsyncWriter()
        if is_seed_fix:
            random.seed(2)
        self.is_seed_fix = is_seed_fix
        self.current_image = None
        self.current_geoimage = None
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()
        self.writer.close()

    def get_random_images(self, number: int, line_strings, overwrite=False, show_progress=True):
        geo_lines = GeoLines(line_strings)
        image_number = self._get_image_number(overwrite)
        points = geo_lines.random_points(number - image_number)
        Image.MAX_IMAGE_PIXELS = 20000 * 20000

        points_by_image = {}
        for point in points:
            points_by_image.setdefault(self._find_ortho_photo(point), []).append(point)

        if show_progress:
            widgets = [
                ' [', os.path.basename(os.path.normpath(self.out_path)), '] ',
                progressbar.Percentage(), ' ',
                progressbar.SimpleProgress(), ' ',
                progressbar.Bar(),
                progressbar.Timer(), ' ',
                progressbar.ETA()
            ]
        else:
            widgets = []

        with progressbar.ProgressBar(max_value=number, widgets=widgets) as bar:
            for key, value in points_by_image.items():
                try:
                    for point in value:
                        sample = self._get_sample_image(point=point, image_path=key)
                        self.writer.write(sample, os.path.join(self.out_path, '{0:04d}.png'.format(image_number)))
                        image_number += 1
                        bar.update(image_number)
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

    def _get_sample_image(self, point: GeoPoint, image_path: str) -> Image:
        if image_path is None:
            raise ValueError('Could not find an Orthophoto for {0} x {1}'.format(point.north, point.east))
        if not self.current_image or self.current_image.filename != image_path:
            self.current_geoimage = GeoDataProvider(geo_tiff_path=image_path)
            self.current_image = Image.open(image_path)

        x, y = self.current_geoimage.geo_point_to_pixel(point)

        if not 0 <= x <= self.current_image.size[0] or not 0 <= y <= self.current_image.size[1]:
            raise ValueError('GeoPoint {0} is outside Orthophoto {1}'.format(point, image_path))

        return self.current_image.crop((x - self.image_size / 2, y - self.image_size / 2, x + self.image_size / 2, y + self.image_size / 2))

    def _get_image_number(self, overwrite: bool):
        image_number = 0
        if not overwrite:
            image_number = sum([len(files) for r, d, files in os.walk(self.out_path)])
        if self.is_seed_fix and image_number > 0:
            print("you set flag is_seed_fix = false, override = false and you already have some images in your dir. The new images will may be the same images like you already have, please dubblecheck if it's what you want.")
        return image_number
