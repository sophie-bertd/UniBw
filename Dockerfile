FROM mundialis/esa-snap:ubuntu

RUN apt-get upgrade && apt-get update
RUN pip install --upgrade pip && pip install setuptools tqdm

COPY /dinsargeocoder dinsargeocoder
WORKDIR /dinsargeocoder
RUN python3 setup.py bdist_wheel
RUN pip install .

WORKDIR /
COPY /geocoding geocoding

WORKDIR /geocoding
RUN python3 main.py