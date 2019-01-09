## select version with or without GPU support, if you like gpu support u need to have install CUDA drivers.
# FROM tensorflow/tensorflow:latest-gpu-py3
FROM tensorflow/tensorflow:latest-py3

WORKDIR /usr/src/app/src

# This enables imports to always find our modules defined in "src"
ENV PYTHONPATH "/usr/src/app/src"

RUN echo "alias py=python" > ~/.bash_aliases

RUN apt-get update \
 && apt-get --assume-yes install \
  libgdal-dev \
  gdal-bin \
  git \
  npm \
  osmosis \
  python3-gdal \
 && rm -rf /var/lib/apt/lists

RUN ln -s /usr/bin/nodejs /usr/bin/node \
 && npm install -g osmtogeojson

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
