#!/bin/bash

command -v docker > /dev/null 2>&1 || { echo >&2  "Docker is not installed on the machine. Please install first"; exit 1; }

DIR_NAME=$(basename $(pwd))
CONTAINER_ZOOKEEPER_ID=$(docker ps -a -q -f "name=${DIR_NAME}_zookeeper_1")
CONTAINER_KAFKA1_ID=$(docker ps -a -q -f "name=${DIR_NAME}_kafka1_1")
CONTAINER_KAFKA2_ID=$(docker ps -a -q -f "name=${DIR_NAME}_kafka1_1")

SENTIMENT_TOPICS=("SaluteToService-sentiment"
"SimonFraserUniversity-sentiment"
"Interesting-topics-sentiment"
"BigData-sentiment"
"noshavenovember-sentiment"
"Christmas-sentiment"
"Trudeau-sentiment"
"Canada-sentiment"
"Vancouver-sentiment"
"Midterms-sentiment"
"Trump-sentiment"
"POTUS-sentiment"
"MulledWine-sentiment"
"Snow-sentiment"
"Cold-sentiment"
"Caravan-sentiment"
"-ff-sentiment"
"-followfriday-sentiment"
"-followback-sentiment"
"-giveaway-sentiment"
"-contest-sentiment"
"-win-sentiment"
"-competition-sentiment"
"-crypto-sentiment"
"-ico-sentiment"
"-bitcoin-sentiment"
"-funny-sentiment"
"-photography-sentiment"
"-pets-sentiment"
)

if [[ ! -z "$CONTAINER_KAFKA1_ID" && ! -z "$CONTAINER_KAFKA2_ID" ]]; then
    echo "Creating topics..."
    for topic in "${SENTIMENT_TOPICS[@]}"; do
        docker exec "$CONTAINER_KAFKA1_ID" kafka-topics.sh --zookeeper zookeeper:2181 --create --if-not-exists --replication-factor 2 --partitions 1 --topic "${topic}"
    done
else
    echo >&2 "Both containers for kafka must exist but at least one of them doesn't. Please bring them up with docker-compose first"; exit 1;
fi

echo
echo "Listing topics available..."
docker exec "$CONTAINER_KAFKA1_ID" kafka-topics.sh --zookeeper zookeeper:2181 --list