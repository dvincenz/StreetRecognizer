import argparse
import os

import geojson
import json

from micromodel import micromodel

def _parse_args():
    parser = argparse.ArgumentParser(description='Makes predictions based on previously generated prediction data using the micromodel.')
    parser.add_argument('model', type=str, help='name of the saved micromodel to use')
    parser.add_argument('-i', '--input', type=str, default='../data/in/micro-predict', help='directory path to read the prediction images from')
    parser.add_argument('-o', '--output', type=str, default='../data/out/micro-predict.json', help='geojson file to write')
    parser.add_argument('--confidence', type=float, default=0.7, help='minimum confidence required to include a prediction in the result (default: 0.7)')
    parser.add_argument('--osm', type=str, default='../data/in/osm/unlabeled-ways-filtered.json', help='path to osm geojson file containing the street data for the predicted streets')
    return vars(parser.parse_args())

def run():
    args = _parse_args()

    prediction_file = os.path.join('../data/out', '{0}.json'.format(args['model']))
    micromodel(
        name=args['model'],
        num_classes=2,
        predict=args['input'],
        out=prediction_file
    )

    with open(prediction_file, mode='r', encoding='UTF-8') as file:
        prediction_result = json.load(file)

    all_predictions_by_street = _get_all_predictions_by_street(prediction_result)
    final_prediction_by_street = _get_final_prediction_by_street(all_predictions_by_street, args['confidence'])

    with open(args['osm'], mode='r', encoding='UTF-8') as file:
        osm_geojson = geojson.load(file)

    for street_id, predicted_surface in final_prediction_by_street.items():
        for feature in osm_geojson['features']:
            if isinstance(feature.geometry, geojson.LineString) and feature['id'] == 'way/{0}'.format(street_id):
                feature['properties']['surface'] = predicted_surface

    with open(args['output'], mode='w+', encoding='UTF-8') as file:
        geojson.dump(obj=osm_geojson, fp=file, indent=4)

    print('Result written to {0}'.format(os.abspath(args['output'])))

def _get_all_predictions_by_street(prediction_result) -> dict:
    result = {}
    for prediction in prediction_result['predictions']:
        street_id = os.path.basename(os.path.dirname(prediction['image']))
        result.setdefault(street_id, []).append(prediction['values'])

    return result

def _get_final_prediction_by_street(predictions_by_street, min_confidence: float) -> dict:
    result = {}
    for street_id, predictions in predictions_by_street.items():
        predicted_surfaces = {}
        for prediction in predictions:
            (surface, confidence) = _max_unique(prediction)
            if surface and confidence >= min_confidence:
                predicted_surfaces.setdefault(surface, 0)
                predicted_surfaces[surface] += 1

        (surface, _) = _max_unique(predicted_surfaces)
        if surface:
            result[street_id] = surface

    return result


def _max_unique(dictionary) -> (object, object):
    max_item = None
    max_value = None
    for key, value in dictionary.items():
        if max_item is None or value > max_value:
            max_item = key
            max_value = value

    for key, value in dictionary.items():
        if value == max_value and key != max_item:
            print('Non-Unique result found: ({0} / {1}, {2})'.format(key, max_item, value))
            return (None, max_value)

    return (max_item, max_value)

if __name__ == "__main__":
    run()
