import os
import sqlite3

class TileMetaExtractor:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    def insert_tiles(self, tile_data: dict):
        surfaces = set()
        tiles = set()
        tiles_surfaces = set()

        for tile in tile_data['tiles']:
            tile_name = tile['tileName']
            file_path = os.path.join(tile_data['tileDirectory'], tile['tileName'])

            for way in tile['ways']['features']:
                if 'surface' in way['properties']:
                    surfaces.add((way['properties']['surface'],))
                    tiles_surfaces.add((file_path, way['properties']['surface']))
                else:
                    tiles_surfaces.add((file_path, None))

            tiles.add((
                file_path,
                tile_name
            ))

        self._cursor.executemany('INSERT OR IGNORE INTO surfaces VALUES (?)', list(surfaces))
        self._cursor.executemany('INSERT OR REPLACE INTO tiles VALUES (?,?)', list(tiles))
        self._cursor.executemany('INSERT OR IGNORE INTO tiles_surfaces VALUES (?,?)', list(tiles_surfaces))


    def print_tile_information(self):
        num_tiles_with_surfaces = self._cursor.execute('SELECT COUNT(DISTINCT file_path) FROM tiles_surfaces WHERE surface IS NOT NULL').fetchone()[0]
        num_tiles_without_surfaces = self._cursor.execute('SELECT COUNT(DISTINCT file_path) FROM tiles_surfaces WHERE surface IS NULL').fetchone()[0]
        num_tiles_with_and_without_surfaces = self._cursor.execute('''
            SELECT COUNT(DISTINCT ts.file_path) FROM
                (SELECT DISTINCT file_path AS fp FROM tiles_surfaces WHERE surface IS NULL)
                JOIN tiles_surfaces ts ON ts.file_path = fp
                WHERE ts.surface IS NOT NULL
        ''').fetchone()[0]
        num_tiles_with_only_labeled_surfaces = self._cursor.execute('''
            SELECT COUNT(DISTINCT ts.file_path) FROM tiles_surfaces ts
                WHERE ts.surface IS NOT NULL
                AND (SELECT COUNT(*) FROM tiles_surfaces ts2
                    WHERE ts.file_path = ts2.file_path
                    AND ts2.surface IS NULL) = 0
        ''').fetchone()[0]
        num_tiles_with_only_unlabeled_surfaces = self._cursor.execute('''
            SELECT COUNT(DISTINCT ts.file_path) FROM tiles_surfaces ts
                WHERE ts.surface IS NULL
                AND (SELECT COUNT(*) FROM tiles_surfaces ts2
                    WHERE ts.file_path = ts2.file_path
                    AND ts2.surface IS NOT NULL) = 0
        ''').fetchone()[0]
        num_tiles_without_ways = self._cursor.execute('SELECT COUNT(*) FROM tiles t WHERE (SELECT COUNT(*) FROM tiles_surfaces ts WHERE t.file_path = ts.file_path) = 0').fetchone()[0]
        num_tiles = self._cursor.execute('SELECT COUNT(*) FROM tiles').fetchone()[0]

        print('Tiles with labeled surfaces: ' + str(num_tiles_with_surfaces))
        print('Tiles with unlabeled surfaces: ' + str(num_tiles_without_surfaces))
        print('Tiles with labeled and unlabeled surfaces: ' + str(num_tiles_with_and_without_surfaces))
        print('Tiles with only labeled surfaces: ' + str(num_tiles_with_only_labeled_surfaces))
        print('Tiles with only unlabeled surfaces: ' + str(num_tiles_with_only_unlabeled_surfaces))
        print('Tiles without ways: ' + str(num_tiles_without_ways))
        print('Total tiles: ' + str(num_tiles))
