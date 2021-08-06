FROM ubuntu:20.04

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install python3 python3-pip firefox-geckodriver
RUN DEBIAN_FRONTEND="noninteractive" pip install --upgrade --no-cache-dir --prefer-binary -Iv selenium Pillow==8.3.1

WORKDIR /app

COPY scripts/entrypoint.sh .
COPY scripts/make_gif.py .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
