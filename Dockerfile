FROM python:3.11-slim-bullseye

RUN pip3 install --no-cache-dir balcony

ENTRYPOINT [ "balcony" ]