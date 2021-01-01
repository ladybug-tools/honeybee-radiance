FROM python:3.7

LABEL maintainer="Ladybug Tools" email="info@ladybug.tools"

# Create non-root user
RUN adduser ladybugbot --uid 1000 --disabled-password --gecos ""
USER ladybugbot
WORKDIR /home/ladybugbot

# Install radiance
ENV RAYPATH=/home/ladybugbot/lib
ENV PATH="/home/ladybugbot/bin:${PATH}"
RUN curl -L https://ladybug-tools-releases.nyc3.digitaloceanspaces.com/Radiance_5.3a.fc2a2610_Linux.zip --output radiance.zip \
&& unzip -p radiance.zip | tar xz \
&& mkdir bin \
&& mkdir lib \
&& mv ./radiance-5.3.fc2a261076-Linux/usr/local/radiance/bin/* /home/ladybugbot/bin \
&& mv ./radiance-5.3.fc2a261076-Linux/usr/local/radiance/lib/* /home/ladybugbot/lib \
&& rm -rf radiance-5.3.fc2a261076-Linux \
&& rm radiance.zip

# Install honeybee-radiance cli
ENV PATH="/home/ladybugbot/.local/bin:${PATH}"
COPY . honeybee-radiance
RUN pip3 install setuptools wheel \
    && pip3 install pydantic==1.7.3 honeybee-schema ./honeybee-radiance[cli]

# Set workdir
RUN mkdir -p /home/ladybugbot/run
WORKDIR /home/ladybugbot/run
