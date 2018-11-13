#!/bin/bash

command -v docker > /dev/null 2>&1 || { echo >&2  "Docker is not installed on the machine. Please install first"; exit 1; }

docker run --rm -d -p 8080:10080 bigdata-project-tornado:latest