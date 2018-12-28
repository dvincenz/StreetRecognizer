## select version with or without GPU support, if you like gpu support u need to have install CUDA drivers.
# FROM tensorflow/tensorflow:latest-gpu-py3
FROM tensorflow/tensorflow:latest-py3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt-get update
RUN apt-get -y install libgdal-dev
RUN apt install gdal-bin
RUN apt install python3-gdal
RUN pip install --no-cache-dir -r requirements.txt

RUN echo "alias py=python" > ~/.bash_aliases


#start docker
#docker build -t challp .
#docker run -v /mnt/hgfs/Repos/HSR/challangeProject/StreetRecognizer/src:/usr/src/app -it challp bash
