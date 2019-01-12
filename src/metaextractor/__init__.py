import argparse
import json
import os
import pandas
import sqlite3

from metaextractor.OrthoMetaExtractor import OrthoMetaExtractor
from metaextractor.TileMetaExtractor import TileMetaExtractor


def _parse_args():
    parser = argparse.ArgumentParser(description='Extract relevant metadata from Ortho-Photos and -Tiles and store them in a database for easier access.')
    parser.add_argument('datasource', metavar='DB', type=str, help='path to the database file')
    parser.add_argument('-o', '--ortho-data', type=str, help='path to the ortho photos to index')
    parser.add_argument('-t', '--tile-data', type=str, help='path to the JSON containing the tile data for an ortho photo')
    parser.add_argument('--clean', action='store_true', help='Cleans (drops) the database and re-initializes it')
    parser.add_argument('--dump', metavar='TABLE', help='Dumps the content of the given table, instead of extracting and inserting any data')
    return vars(parser.parse_args())


def run():
    args = _parse_args()
    extractor(
        ortho_data_path=args['ortho_data'],
        tile_data_path=args['tile_data'],
        data_source_path=args['datasource'],
        clean=args['clean'],
        dump=args['dump']
    )


def _init_db(cursor: sqlite3.Cursor):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, 'init.sql'), 'r') as initfile:
        query = initfile.read()

    cursor.executescript(query)
    print('Database initialized!')


def extractor(ortho_data_path: str, tile_data_path: str, data_source_path: str, clean: bool = False, dump: str = None):
    if os.path.exists(data_source_path):
        if clean:
            os.remove(data_source_path)
            print('Database deleted!')
        else:
            print('Database found, will not be cleaned')
    else:
        print('Database not found, nothing to clean!')

    conn = sqlite3.connect(data_source_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    if cursor.fetchone() is None:
        _init_db(cursor)

    if not dump is None:
        # Yes, yes, SQL Injection, but table-name is not parameterizable in sqlite3
        print(pandas.read_sql_query("SELECT * FROM " + dump, conn))
        return 0

    if ortho_data_path:
        print('Extracting ortho metadata...')
        ortho_extractor = OrthoMetaExtractor(cursor)
        ortho_extractor.insert_orthos(ortho_data_path)
    else:
        print('--ortho-data not provided; skipping ortho-image meta extraction')

    if tile_data_path:
        print('Extracting tile metadata...')
        with open(tile_data_path, 'r') as infile:
            tile_data = json.load(infile)

        tile_extractor = TileMetaExtractor(cursor)
        tile_extractor.insert_tiles(tile_data)
        tile_extractor.print_tile_information()
    else:
        print('--tile-data not provided; skipping ortho-tile meta extraction')

    conn.commit()
    conn.close()
    return 0


if __name__ == "__main__":
    run()
