# StreetRecognizer
Proof of concept to recognize and attribute streets/roads or trails surfaces based on orthophotos and machine learning

## Environment

### Prerequisites

We created a docker image for easier development, so there is no need to install all Python libraries locally. 
- You need [Docker](https://www.docker.com/) installed on your system. 
- You may need access to [swisstopo](https://www.swisstopo.admin.ch/) or similar images to be able to make use of our model one-to-one. 

### Build

```bash
docker build -t street-recognizer .
```

### Run

The commands below will run the docker image and mount your local workspace into the image, so you can execute changes to the files live inside the container.

Linux:

```bash
docker run -v $(pwd):/usr/src/app -it street-recognizer bash
```

Windows (PowerShell):

```powershell
docker run -v "$(Get-Location):/usr/src/app" -it street-recognizer bash
```

## Development

### Slicer

#### Usage

```bash
py Slicer -h
```

#### Example

```bash
py Slicer ../data/in/Ortho/DOP25_LV95_1091-14_2013_1_13.tif ../data/out
```

### Image provider
The image provider, downloads images from an azure blob storage and convert the images from LV95 to WGS84 coordinate system. You don't need to have an azure account, you can also provide the images locally.

#### Usage
```bash
py ImageProvider -h
```

#### Example
```bash
py ImageProvider 1195-22
```

### Example in Python 

You can use this module in python as single executor, the same way as you use it in the console
```python
import ImageProvider

ImageProvider.Provider(imageNumber="1151-22", azureaccount="swisstopo")
```

The other possibility is to use the module as object for advanced usage
```python
import ImageProvider
from ImageProvider import ImageProviderConfig

config = ImageProviderConfig(azure_blob_account="swisstopo")
images = ImageProvider.Provider(config=config)
images.get_image("185-34")

```

## Osm data provider
Provides osm data for a defined coordinate area, or for the coordinates of a gifTiff image

### usage in console
```bash
py OsmDataProvider -h
```

### Example in console
```bash
py OsmDataProvider ../data/in/osm/vector -p ../data/in/ortho/wgs84/DOP25_LV95_2240-33_2015_1_15.tif
```

### Example in Python

You can use this module in python as single executor, the same way as you use it in the console
```python
import OsmDataProvider
OsmDataProvider.Provider(target="../data/in/osm/vector", imagepath="../data/in/ortho/wgs84/DOP25_LV95_2240-33_2015_1_15.tif")
```

The other possibility is to use the module as object for advanced usage
```python
import OsmDataProvider
from OsmDataProvider import OsmDataProviderConfig

config = OsmDataProviderConfig(output_path = "../data/in/osm/vector", buffer={})
osmData = OsmDataProvider.Provider(config=config)
osmData.export_ways_by_image('../data/in/ortho/wgs84/DOP25_LV95_2240-33_2015_1_15.tif')

```

## Model
You can find [here](model.md) some details about the model.
