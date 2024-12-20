#!/bin/bash

docker build --platform linux/amd64 -t rp-visual:v1 .

docker tag rp-visual:v1  mapsanalytics.azurecr.io/rp-visual:v1

docker push  mapsanalytics.azurecr.io/rp-visual:v1

