from abc import ABC, abstractmethod
from collections import OrderedDict
import os

import json
import keras
import numpy
from PIL import Image

class ModelMicro(ABC):
    def __init__(self, num_classes: int, model_path: str):
        self.num_classes = num_classes
        self._model_path = model_path

    def predict(self, input_path: str, output_file: str):
        data = []
        images = []

        if os.path.isdir(input_path):
            for dirpath, _, filenames in os.walk(input_path):
                for file in filenames:
                    if os.path.splitext(file)[1] == '.png':
                        image = Image.open(os.path.join(dirpath, file))
                        data.append(list(image.getdata()))
                        images.append(os.path.abspath(os.path.join(dirpath, file)))
            print('Collected {0} images for predictions'.format(len(images)))

        else:
            image = Image.open(input_path)
            data.append(list(image.getdata()))
            images.append(os.path.abspath(input_path))

        x_predict = numpy.array(data).reshape(len(data), 32, 32, 3)

        self._predict(
            x_predict=x_predict,
            image_names=images,
            output_file=output_file
        )

    def _predict(self, x_predict: numpy.array, image_names: [str], output_file: str):
        model = keras.models.load_model(self._model_path)
        y_predict = model.predict_proba(x_predict)

        paved = 0
        unpaved = 0
        predictions = []

        for i, prediction in enumerate(y_predict):
            if prediction[0] >= 0.5:
                paved += 1
            else:
                unpaved += 1

            predictions.append(self._format_prediction(
                image_name=image_names[i],
                prediction=prediction
            ))

        data = OrderedDict([
            ('model', self._model_path),
            ('summary', OrderedDict([
                ('total', len(x_predict)),
                ('paved', paved),
                ('unpaved', unpaved)
                ])),
            ('predictions', predictions)
        ])

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, mode='w', encoding='UTF-8') as file:
            json.dump(data, file, indent=4)

        print('Predictions saved to {0}'.format(output_file))
        print(json.dumps(data['summary'], indent=4))

    def _format_prediction(self, image_name: str, prediction):
        data = OrderedDict([
            ('image', image_name)
        ])
        values = OrderedDict()
        result = "Unknown"
        max_value = 0
        for surface in range(self.num_classes):
            key = self._map_int_to_surface(surface)
            value = prediction[surface].item()
            values.update([(key, value)])
            if value > max_value:
                result = key
                max_value = value

        data.update([('values', values), ('prediction', result)])
        return data

    @abstractmethod
    def _map_int_to_surface(self, number: int) -> str:
        pass
