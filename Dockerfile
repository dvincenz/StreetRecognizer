## select version with or without GPU support, if you like gpu support u need to have install CUDA drivers.
# FROM tensorflow/tensorflow:latest-gpu-py3
FROM tensorflow/tensorflow:latest-py3

WORKDIR /usr/src/app

RUN echo "alias py=python" > ~/.bash_aliases

RUN apt-get update \
 && apt-get --assume-yes install \
  libgdal-dev \
  gdal-bin \
  python3-gdal \
 && rm -rf /var/lib/apt/lists

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt


#start docker
#docker build -t challp .
#docker run -v /mnt/hgfs/Repos/HSR/challangeProject/StreetRecognizer/src:/usr/src/app -it challp bash
