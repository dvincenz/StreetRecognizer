# StreetRecognizer

Proof of concept to recognize and attribute streets/roads or trails surfaces based on orthophotos and machine learning.

To get started with developing, see the [Developer Guide](./developer-guide.md).

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

## Deprecated Modules

### Slicer

The slicer was originally intended to slice an ortho photo into tiles of e.g. 1024x1024 pixels. The idea being our model would work with these larger tiles, however this proved too problematic for many reasons detailed in [Model Ideas](./model.md).

#### Usage

```bash
py slicer -h
```

#### Example

```bash
py slicer ../data/in/ortho/wgs84/DOP25_LV95_1091-14_2013_1_13.tif ../data/out
```
