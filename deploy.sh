#!/bin/sh

if [ -n "$1" ]
then
  NEXT_RELEASE_VERSION=$1
else
  echo "A release version must be supplied"
  exit 1
fi

CONTAINER_NAME="ladybugtools/honeybee-radiance"

echo "PyPi Deployment..."
echo "Building distribution"
python setup.py sdist bdist_wheel
echo "Pushing new version to PyPi"
twine upload dist/* -u $PYPI_USERNAME -p $PYPI_PASSWORD

export radiance_version='5.3a.fc2a2610'

curl -L "https://ladybug-tools-releases.nyc3.digitaloceanspaces.com/Radiance_${radiance_version}_Linux.zip" --output radiance.zip

unzip -p radiance.zip | tar xz

echo "Docker Deployment..."
echo "Login to Docker"
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

docker build . -t $CONTAINER_NAME:$NEXT_RELEASE_VERSION --build-arg radiance_version=${radiance_version}
docker tag $CONTAINER_NAME:$NEXT_RELEASE_VERSION $CONTAINER_NAME:latest

docker push $CONTAINER_NAME:latest
docker push $CONTAINER_NAME:$NEXT_RELEASE_VERSION
