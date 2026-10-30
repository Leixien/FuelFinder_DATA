FROM python:3.13-slim

RUN apt-get update \
    && apt-get install --yes --no-install-recommends curl git openssh-client ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Rome
WORKDIR /app
COPY build_stations.py deploy/publish.sh ./
RUN chmod +x publish.sh

ENTRYPOINT ["/app/publish.sh"]
