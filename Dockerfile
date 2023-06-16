FROM debian:12.0

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install curl jq python3 python3-pip firefox-esr libwebp-dev

WORKDIR /app
COPY requirements.txt .

RUN DEBIAN_FRONTEND="noninteractive" pip install --upgrade --no-cache-dir --prefer-binary -Iv -r /app/requirements.txt --break-system-packages

COPY scripts/install_geckodriver.sh .
COPY scripts/entrypoint.sh .
COPY scripts/make_gif.py .

RUN bash ./install_geckodriver.sh
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
