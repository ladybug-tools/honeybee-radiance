FROM python:3.7

WORKDIR /tmp/
RUN curl -L https://github.com/MingboPeng/Radiance/releases/download/v5.5.2/Radiance_5.5.2_Linux.zip --output radiance.zip \
&& unzip -p radiance.zip | tar xz \
&& mv ./radiance-Linux/usr/local/radiance/bin/* /usr/local/bin \
&& mv ./radiance-Linux/usr/local/radiance/lib/* /usr/local/lib \
&& rm -rf `ls`

ENV RAYPATH=/usr/local/lib

WORKDIR /usr/app/

COPY . .
RUN pip install .[cli]

WORKDIR /opt/run-folder/
