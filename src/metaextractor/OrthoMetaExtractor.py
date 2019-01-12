import os
import re
import sqlite3

from geodataprovider.GeoDataProvider import GeoDataProvider

class OrthoMetaExtractor:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    def insert_orthos(self, ortho_path: str):
        orthos = []
        for filename in os.listdir(ortho_path):
            if os.path.splitext(filename)[1].find('tif') >= 0:
                ortho_file_path = os.path.join(ortho_path, filename)
                geo_provider = GeoDataProvider(geo_tiff_path=ortho_file_path)
                rect = geo_provider.get_bounding_rect()
                width, height = geo_provider.get_pixel_size()
                orthos.append((
                    self._get_image_number(filename),
                    ortho_file_path,
                    width,
                    height,
                    min(rect.a.east, rect.b.east),
                    max(rect.a.east, rect.b.east),
                    min(rect.a.north, rect.b.north),
                    max(rect.a.north, rect.b.north)
                ))

        self._cursor.executemany('INSERT OR IGNORE INTO orthos VALUES (?,?,?,?,?,?,?,?)', orthos)
        print('Inserted {0} ortho rows'.format(self._cursor.rowcount))
    
    @staticmethod
    def _get_image_number(ortho_file_name: str):
        match = re.match('DOP25_LV95_(\d{4}-\d{2})_\d+_\d+_\d+\.tiff?', ortho_file_name)
        return match.group(1)
