#!/bin/bash

command -v docker > /dev/null 2>&1 || { echo >&2  "Docker is not installed on the machine. Please install first"; exit 1; }

CONTAINER_ID="$1"
ID_EXISTS=$(docker ps -a -q -f "id=$CONTAINER_ID")

if [[ "$ID_EXISTS" == "$CONTAINER_ID" ]]; then
    docker stop "$CONTAINER_ID"
else
    echo >&2 "Container ID $CONTAINER_ID does not exist. Failed to stop"; exit 1;
fi