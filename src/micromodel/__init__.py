import argparse
import os

from micromodel.ModelMicro2 import ModelMicro2
from micromodel.ModelMicro8 import ModelMicro8
from micromodel.ModelMicro10 import ModelMicro10

def _parse_args():
    parser = argparse.ArgumentParser(description='Creates and optionally trains a MicroModel, or uses an existing MicroModel to make predictions.')
    parser.add_argument('name', type=str, help='name of the model (used as file name)')
    parser.add_argument('-i', '--input', type=str, default='../data/in/micro', help='directory path to read the training/test images from')
    parser.add_argument('--new', '--create', action='store_true', help='create a new model')
    parser.add_argument('-n', '--num-classes', type=int, default=2, help='number of classes to classify (default: 2)')
    parser.add_argument('--train', action='store_true', help='train the given model')
    parser.add_argument('--train-percent', type=float, default=0.5, help='percentage of data to use as training data; remainder will be used as test data (default: 0.5)')
    parser.add_argument('--predict', type=str, help='make predictions for the given image or directory of images')
    parser.add_argument('-o', '--out', type=str, help='output json file to write predictions to')
    return vars(parser.parse_args())

def _run():
    args = _parse_args()
    micromodel(**args)

def micromodel(**kwargs):
    model_name = '{0}.h5'.format(kwargs.get('name'))

    if kwargs.get('new'):
        if kwargs.get('num_classes') == 2:
            model = ModelMicro2.create_untrained(model_name)
        elif kwargs.get('num_classes') == 8:
            model = ModelMicro8.create_untrained(model_name)
        elif kwargs.get('num_classes') == 10:
            model = ModelMicro10.create_untrained(model_name)
        else:
            raise ValueError('No model found for {0} classes'.format(kwargs.get('num_classes')))

    else:
        if kwargs.get('num_classes') == 2:
            model = ModelMicro2.load(model_name)
        elif kwargs.get('num_classes') == 8:
            model = ModelMicro8.load(model_name)
        elif kwargs.get('num_classes') == 10:
            model = ModelMicro10.load(model_name)
        else:
            raise ValueError('No model found for {0} classes'.format(kwargs.get('num_classes')))

    if kwargs.get('train'):
        model.train(micro_image_dir=kwargs.get('input'), train_percentage=kwargs.get('train_percent'))

    if kwargs.get('predict'):
        out_file = kwargs.get('out')
        if not out_file:
            out_file = os.path.join('..', 'data', 'out', '{0}.json'.format(kwargs.get('name')))
            print('--out not specified, using {0}'.format(out_file))
        model.predict(input_path=kwargs.get('predict'), output_file=out_file)

if __name__ == "__main__":
    _run()
