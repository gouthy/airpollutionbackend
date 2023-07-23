FROM ghcr.io/osgeo/gdal:ubuntu-small-3.7.1

RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install --no-cache gdal numpy

CMD ["python3"]
