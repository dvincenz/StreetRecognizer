# StreetRecognizer

Proof of concept to recognize and attribute streets/roads or trails surfaces based on orthophotos and machine learning

## Development

We created a docker image for easier development, so there is no need to install all Python libraries locally.

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

## Slicer

### Usage

```bash
py Slicer -h
```

### Example

```bash
py Slicer ../data/in/Ortho/DOP25_LV95_1091-14_2013_1_13.tif ../data/out
```
