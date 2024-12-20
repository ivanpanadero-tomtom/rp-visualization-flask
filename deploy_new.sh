#!/bin/bash

docker build --platform linux/amd64 -t pois-rp-visual:v1 .

docker tag rp-visual:v1 crdacr01madev.azurecr.io/pois-rp-visual:v1

docker push crdacr01madev.azurecr.io/pois-rp-visual:v1