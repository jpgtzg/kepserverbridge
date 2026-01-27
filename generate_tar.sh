#!/bin/bash

docker build -t kepserverbridge .
docker save kepserverbridge -o kepserverbridge.tar