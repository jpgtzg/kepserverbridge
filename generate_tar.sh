#!/bin/bash

docker build -t kepserverbridge .

docker save kepserverbridge:latest -o kepserverbridge.tar