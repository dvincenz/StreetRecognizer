# StreetRecognizer

Proof of concept to recognize and attribute streets/roads or trails surfaces based on orthophotos and machine learning.

To get started with developing, see the [Developer Guide](./developer-guide.md).

We have also written a [general summary](./summary.md) of the work process and our thoughts on this project.

## Full Process

The full process encompasses acquiring ortho photos, preparing the input data, training the model, and using the model to make predictions. This process is split into multiple modules, of which some steps must be executed manually.

The process can be summarized into the following steps:

1) Acquire ortho photos
2) Generate training data samples
3) Train and save the model
4) Generate image samples of the streets to predict
5) Make predictions using the saved model

### Acquire Ortho Photos

The image provider, downloads images from an azure blob storage and converts the images from LV95 to WGS84 coordinate system. You don't need to have an azure account, you can also provide the images locally.

This must be done for all photos you want to use in training or making predictions.

#### Example

```bash
py imageprovider 1195-22
```

### Generate training data samples

First, the ortho photo metadata must be extracted into a database for easier lookup:

```bash
py metaextractor --ortho-data /swissimage/wgs84 ../data/metadata.db
```

Then, we need to generate the training (and test) data sets:  

```bash
py TrainingDataGenerator.py --pbf ../data/in/osm/switzerland-exact.osm.pbf
```

The `switzerland_exact.osm.pbf` file can be obtained from [planet.osm.ch](https://planet.osm.ch/):

```bash
wget https://planet.osm.ch/switzerland-exact.osm.pbf -O ../data/in/osm/switzerland-exact.osm.pbf
```

### Train and save the model

There are three different models to choose from:

**Binary Model**: Classifies an image into either paved or unpaved.
**Octal Model**: Classifies an image into the 8 most common sub-types of paved or unpaved.
**Decimal Model**: Classifies an image into the 10 most common surfaces.

We recommend using the binary model, as it has the highest accuracy:

```bash
py micromodel binary --num-classes 2 --new --train
```

### Generate prediction images

Since there are many unlabeled ways and the performance of this script is not yet fully optimized, we recommend limiting the number of prepared streets to a reasonable number.

```bash
py PredictionDataGenerator.py -n 300
```

Note that this will actually prepare N streets for every partition (default 25). However, many streets will be duplicated, leading to less than 25*N streets in total in the end.

### Make predictions

To finally make predictions for all prepared ways, do the following:

```bash
py Predictor.py binary --num-classes 2
```

This will output a final geojson at `../data/out/micro-predict.json`, ready to be displayed at e.g. [geojson.io](https://geojson.io).

## Detailed Usage

The above "Full Process" has some abstractions built-in, so the user does not have to use every python module explicitly. However, this can still be done, if desired. Every python module used along the way is accessible through the command line. Every module supports the `-h` and `--help` parameters outlining their usage.

## Deprecated Modules

### Slicer

The slicer was originally intended to slice an ortho photo into tiles of e.g. 1024x1024 pixels. The idea being our model would work with these larger tiles, however this proved too problematic for many reasons detailed in [Model Ideas](./model.md).

#### Usage

```bash
py slicer -h
```

#### Example

```bash
py slicer /swissimage/wgs84/DOP25_LV95_1091-14_2013_1_13.tif ../data/out
```

### ImageProcessor

The ImageProcessor was originally intended to take a geojson file with the osm street data of an ortho photo section. This geojson files contain the street data in a vector format. Then, the ImageProcessor would generate a rasterized image of this vector data with the same size as the corresponding ortho photo.

In combination with the slicer mentioned above, the goal was to feed both the ortho photo slice, as well as the rasterized street slice to the model. This would hopefully assist the model in identifying where the streets are located on the given ortho slice.

This approach was deprecated in favor of the micro model, which is pretty much guaranteed to only always have one street per image.

#### Usage

```bash
py imageprocessor -h
```

The geojson with the streets of this ortho photo section can be obtained from the `osmdataprovider`.

#### Example

```bash
py imageprocessor ../data/DOP25_LV95_1112-44_2013_1_13_line.json ../data/DOP25_LV95_1112-44_2013_1_13-streets.tif --template /swissimage/wgs84/DOP25_LV95_1112-44_2013_1_13.tif --method rasterizeGeojson
```
