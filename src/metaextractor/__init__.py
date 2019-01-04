import argparse
import json
import os
import sqlite3


def _parse_args():
    parser = argparse.ArgumentParser(description='Extract relevant metadata from Ortho-Tiles and store them in a database for easier access.')
    parser.add_argument('tiledata', metavar='TILEDATA', type=str, help='path to the JSON containing the tile data for an ortho photo')
    parser.add_argument('datasource', metavar='DB', type=str, help='path to the database file')
    parser.add_argument('--clean', action='store_true', help='Cleans (drops) the database and re-initializes it')
    return vars(parser.parse_args())


def run():
    args = _parse_args()
    extractor(
        tile_data_path=args['tiledata'],
        data_source_path=args['datasource'],
        clean=args['clean']
    )


def _init_db(cursor: sqlite3.Cursor):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, 'init.sql'), 'r') as initfile:
        query = initfile.read()

    cursor.executescript(query)
    print('Database initialized!')


def _insert_tiles(cursor: sqlite3.Cursor, tile_data: dict):
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

    cursor.executemany('INSERT OR IGNORE INTO surfaces VALUES (?)', list(surfaces))
    cursor.executemany('INSERT OR REPLACE INTO tiles VALUES (?,?)', list(tiles))
    cursor.executemany('INSERT OR IGNORE INTO tiles_surfaces VALUES (?,?)', list(tiles_surfaces))


def _print_tile_information(cursor: sqlite3.Cursor):
    num_tiles_with_surfaces = cursor.execute('SELECT COUNT(DISTINCT file_path) FROM tiles_surfaces WHERE surface IS NOT NULL').fetchone()[0]
    num_tiles_without_surfaces = cursor.execute('SELECT COUNT(DISTINCT file_path) FROM tiles_surfaces WHERE surface IS NULL').fetchone()[0]
    num_tiles_with_and_without_surfaces = cursor.execute('''
        SELECT COUNT(DISTINCT ts.file_path) FROM
            (SELECT DISTINCT file_path AS fp FROM tiles_surfaces WHERE surface IS NULL)
            JOIN tiles_surfaces ts ON ts.file_path = fp
            WHERE ts.surface IS NOT NULL
    ''').fetchone()[0]
    num_tiles_with_only_labeled_surfaces = cursor.execute('''
        SELECT COUNT(DISTINCT ts.file_path) FROM tiles_surfaces ts
            WHERE ts.surface IS NOT NULL
            AND (SELECT COUNT(*) FROM tiles_surfaces ts2
                WHERE ts.file_path = ts2.file_path
                AND ts2.surface IS NULL) = 0
    ''').fetchone()[0]
    num_tiles_with_only_unlabeled_surfaces = cursor.execute('''
        SELECT COUNT(DISTINCT ts.file_path) FROM tiles_surfaces ts
            WHERE ts.surface IS NULL
            AND (SELECT COUNT(*) FROM tiles_surfaces ts2
                WHERE ts.file_path = ts2.file_path
                AND ts2.surface IS NOT NULL) = 0
    ''').fetchone()[0]
    num_tiles_without_ways = cursor.execute('SELECT COUNT(*) FROM tiles t WHERE (SELECT COUNT(*) FROM tiles_surfaces ts WHERE t.file_path = ts.file_path) = 0').fetchone()[0]
    num_tiles = cursor.execute('SELECT COUNT(*) FROM tiles').fetchone()[0]

    print('Tiles with labeled surfaces: ' + str(num_tiles_with_surfaces))
    print('Tiles with unlabeled surfaces: ' + str(num_tiles_without_surfaces))
    print('Tiles with labeled and unlabeled surfaces: ' + str(num_tiles_with_and_without_surfaces))
    print('Tiles with only labeled surfaces: ' + str(num_tiles_with_only_labeled_surfaces))
    print('Tiles with only unlabeled surfaces: ' + str(num_tiles_with_only_unlabeled_surfaces))
    print('Tiles without ways: ' + str(num_tiles_without_ways))
    print('Total tiles: ' + str(num_tiles))


def extractor(tile_data_path: str, data_source_path: str, clean: bool = False):
    with open(tile_data_path, 'r') as infile:
        tile_data = json.load(infile)

    if clean and os.path.exists(data_source_path):
        os.remove(data_source_path)
        print('Database deleted!')
    else:
        print('Database not found, nothing to clean!')

    conn = sqlite3.connect(data_source_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tiles'")
    if cursor.fetchone() is None:
        _init_db(cursor)

    _insert_tiles(cursor, tile_data)
    _print_tile_information(cursor)

    conn.commit()
    conn.close()
    return 0


if __name__ == "__main__":
    run()
