#!/bin/bash -e

# PYPI_USERNAME - (Requried) Username for the publisher's account on PyPI
# PYPI_PASSWORD - (Required, Secret) Password for the publisher's account on PyPI

cat <<EOF >> ~/.pypirc
[distutils]
index-servers=pypi

[pypi]
username=$PYPI_USERNAME
password=$PYPI_PASSWORD
EOF

# Deploy to pip
python setup.py sdist bdist_wheel
twine upload dist/*

# Rebuild quantrocker/zipline Docker image with latest package
curl -X POST https://registry.hub.docker.com/u/quantrocket/zipline/trigger/8b4a27f7-f537-4a9d-97cd-cbf7ab5508d4/
