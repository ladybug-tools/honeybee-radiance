FROM python:3.7

WORKDIR /tmp/
RUN curl -L https://github.com/NREL/Radiance/releases/download/5.2/radiance-5.2.dd0f8e38a7-Linux.tar.gz | tar xz \
&& mv `ls`/usr/local/radiance/bin/* /usr/local/bin \
&& mv `ls`/usr/local/radiance/lib/* /usr/local/lib \
&& rm -rf `ls`

ENV RAYPATH=/usr/local/lib

WORKDIR /usr/app/

COPY . .
RUN pip install .[cli]

WORKDIR /opt/run-folder/