FROM python:3.7-slim

LABEL maintainer="Ladybug Tools" email="info@ladybug.tools"

ARG radiance_version

ENV WORKDIR='/home/ladybugbot'
ENV RAYPATH='${WORKDIR}/lib'
ENV PATH="${WORKDIR}/.local/bin:${RAYPATH}:${PATH}"

RUN apt-get update \
    && apt-get -y install --no-install-recommends git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN adduser ladybugbot --uid 1000 --disabled-password --gecos ""
USER ladybugbot
WORKDIR ${WORKDIR}

# Expects a decomressed radiance folder in the build context
COPY radiance-${radiance_version}-Linux/usr/local/radiance/bin ${WORKDIR}/bin
COPY radiance-${radiance_version}-Linux/usr/local/radiance/lib ${WORKDIR}/lib

# Install honeybee-radiance
COPY . honeybee-radiance
USER root
RUN pip3 install --no-cache-dir setuptools wheel \
    && pip3 install --no-cache-dir ./honeybee-radiance \
    && apt-get -y --purge remove git \
    && apt-get -y clean \
    && apt-get -y autoremove

USER ladybugbot
# Set workdir
RUN mkdir -p /home/ladybugbot/run
WORKDIR /home/ladybugbot/run
