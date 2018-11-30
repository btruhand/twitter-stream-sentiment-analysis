#!/bin/bash

command -v docker > /dev/null 2>&1 || { echo >&2  "Docker is not installed on the machine. Please install first"; exit 1; }

DIR_NAME=$(basename $(pwd))
CONTAINER_ZOOKEEPER_ID=$(docker ps -a -q -f "name=${DIR_NAME}_zookeeper_1")
CONTAINER_KAFKA1_ID=$(docker ps -a -q -f "name=${DIR_NAME}_kafka1_1")
CONTAINER_KAFKA2_ID=$(docker ps -a -q -f "name=${DIR_NAME}_kafka1_1")

if [[ ! -z "$CONTAINER_KAFKA1_ID" && ! -z "$CONTAINER_KAFKA2_ID" ]]; then
    echo "Deleting topics (including customer offset)..."
    AVAILABLE_TOPICS=$(docker exec $CONTAINER_KAFKA1_ID kafka-topics.sh --zookeeper zookeeper:2181 --list)
    TOPICS_TO_DELETE=$(echo $AVAILABLE_TOPICS | sed 's/\ /,/g')
    docker exec "$CONTAINER_KAFKA1_ID" kafka-topics.sh --zookeeper zookeeper:2181 --delete --topic "$TOPICS_TO_DELETE"
else
    echo >&2 "Both containers for kafka must exist but at least one of them doesn't. Please bring them up with docker-compose first"; exit 1;
fi

echo
echo "Listing topics available..."
docker exec "$CONTAINER_KAFKA1_ID" kafka-topics.sh --zookeeper zookeeper:2181 --list