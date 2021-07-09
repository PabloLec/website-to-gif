FROM ubuntu:20.04

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install python3=3.8.2-0ubuntu2 python3-pip=20.0.2-5ubuntu1.5 firefox-geckodriver=89.0.2+build1-0ubuntu0.20.04.1
RUN DEBIAN_FRONTEND="noninteractive" pip install --upgrade --no-cache-dir --prefer-binary -Iv selenium==3.141.0 Pillow==8.3.1

WORKDIR /app

COPY scripts/entrypoint.sh .
COPY scripts/make_gif.py .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
