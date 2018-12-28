# StreetRecognizer
Proof of concept to recognize and attribute streets/roads or trails surfaces based on orthophotos and machine learning

## Installing enviroment

### Prerequisites

We created a docker image for easier development, so there is no need to install all Python libraries locally. 
- You need only Docker installed on your system. 
- You may need access to swisstopo or similar images to be able to make use of our model one-to-one. (https://www.swisstopo.admin.ch/)

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
The image provider download images from an azure blob storage and convert images from LV95 to WGS84 coordinate system. You dont need to have an azure account, you can also provide the images locally.

#### Usage
```bash
py ImageProvider -h
```

#### Example
```bash
py ImageProvider 1195-22
```

## Model
You can find [here](model.md) some details about the model.
