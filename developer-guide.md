# Developer Guide

## Environment

### HSR Server

For executing code on the HSR server (increased performance), the following command can be used to establish an SSH connection:

```bash
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -p 8080 root@sifs0004.infs.ch
```

*The password is intentionally not included in this documentation.*

### Prerequisites

We created a docker image for easier development, so there is no need to install all Python libraries locally.

- You need [Docker](https://www.docker.com/) installed on your system.
- You may need access to [swisstopo](https://www.swisstopo.admin.ch/) or similar images to be able to make use of our model one-to-one.

To run long during tasks in the background you can use following syntax

```bash
chmod -x TrainingDataGenerator.py
nohup python3 ./TrainingDataGenerator.py &
```

### Build

```bash
docker build -t street-recognizer .
```

### Run

The commands below will run the docker image and mount your local workspace into the image, so you can execute changes to the files live inside the container.

Linux:

```bash
docker run -v $(pwd):/usr/src/app --name street-recognizer -it --rm street-recognizer bash
```

Windows (PowerShell):

```powershell
docker run -v "$(Get-Location):/usr/src/app" --name street-recognizer -it --rm street-recognizer bash
```
