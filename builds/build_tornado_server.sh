#!/bin/bash

command -v docker > /dev/null 2>&1 || { echo >&2  "Docker is not installed on the machine. Please install first"; exit 1; }

docker build --rm -f "../servers/Dockerfile" ../servers