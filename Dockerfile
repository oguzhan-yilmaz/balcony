FROM python:3.13-slim-bullseye

RUN pip3 install --no-cache-dir balcony

ENTRYPOINT [ "balcony" ]