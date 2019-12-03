FROM python:3.6

WORKDIR /tmp/
RUN curl -L https://github.com/NREL/Radiance/releases/download/5.2/radiance-5.2.dd0f8e38a7-Linux.tar.gz | tar xz
RUN mv `ls`/usr/local/radiance/bin/* /usr/local/bin
RUN mv `ls`/usr/local/radiance/lib/* /usr/local/lib
RUN rm -rf `ls`

WORKDIR /usr/app/
# COPY requirements.txt requirements.txt
# RUN pip install -r requirements.txt
COPY . .
RUN pip install -e .[cli]
ENTRYPOINT [ "honeybee-radiance" ]