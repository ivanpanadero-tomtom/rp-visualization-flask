#!/bin/bash

docker build --platform linux/amd64 -t pois-rp-visual .

docker tag pois-rp-visual crdacr01madev.azurecr.io/pois-rp-visual

docker push crdacr01madev.azurecr.io/pois-rp-visual