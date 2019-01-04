import argparse
import json
import os
import sqlite3

def _parse_args():
    parser = argparse.ArgumentParser(description='Extract relevant metadata from Ortho-Tiles and store them in a database for easier access.')
    parser.add_argument('tiledata', metavar='TILEDATA', type=str, help='path to the JSON containing the tile data for an ortho photo')
    parser.add_argument('datasource', metavar='DB', type=str, help='path to the database file')
    return vars(parser.parse_args())

def run():
    args = _parse_args()
    extractor(tile_data_path=args['tiledata'], data_source_path=args['datasource'])

def _init_db(cursor: sqlite3.Cursor):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, 'init.sql'), 'r') as initfile:
        query = initfile.read()

    cursor.execute(query)
    print('Database initialized!')

def extractor(tile_data_path: str, data_source_path: str):
    with open(tile_data_path, 'r') as infile:
        tile_data = json.load(infile)

    conn = sqlite3.connect(data_source_path)
    cursor = conn.cursor()

    #for tile in tile_data['tiles']:
    print(len(tile_data))

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tiles';")
    if cursor.fetchone() is None:
        _init_db(cursor)

    cursor.close()
    return 0

if __name__ == "__main__":
    run()
