import argparse
import os

from micromodel.ModelMicro10 import ModelMicro10

def _parse_args():
    parser = argparse.ArgumentParser(description='Creates and optionally trains a MicroModel, or uses an existing MicroModel to make predictions.')
    parser.add_argument('name', type=str, help='name of the model (used as file name)')
    parser.add_argument('-i', '--input', type=str, default='../data/in/micro', help='directory path to read the training/test images from')
    parser.add_argument('--new', action='store_true', help='create a new model')
    parser.add_argument('--train', action='store_true', help='train the given model')
    parser.add_argument('--train-percent', type=float, default=0.5, help='percentage of data to use as training data; remainder will be used as test data (default: 0.5)')
    return vars(parser.parse_args())

def run():
    args = _parse_args()

    model_name = '{0}.h5'.format(args['name'])

    if args['new']:
        model = ModelMicro10.create_untrained(model_name)

    else:
        model = ModelMicro10.load(model_name)

    if args['train']:
        model.train(micro_image_dir=args['input'], train_percentage=args['train_percent'])

if __name__ == "__main__":
    run()
