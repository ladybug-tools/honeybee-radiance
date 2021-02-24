FROM python:3.7-slim

LABEL maintainer="Ladybug Tools" email="info@ladybug.tools"

ARG radiance_version

ENV WORKDIR='/home/ladybugbot'
ENV RAYPATH='${WORKDIR}/lib'
ENV PATH="${RAYPATH}:${PATH}"

# Create non-root user
RUN adduser ladybugbot --uid 1000 --disabled-password --gecos ""
USER ladybugbot
WORKDIR ${WORKDIR}

COPY radiance-${radiance_version}-Linux/usr/local/radiance/bin ${WORKDIR}/bin
COPY radiance-${radiance_version}-Linux/usr/local/radiance/lib ${WORKDIR}/lib

# Install honeybee-radiance
ENV PATH="/home/ladybugbot/.local/bin:${PATH}"
COPY . honeybee-radiance
RUN pip3 install setuptools wheel \
    && pip3 install ./honeybee-radiance

# Set workdir
RUN mkdir -p /home/ladybugbot/run
WORKDIR /home/ladybugbot/run
