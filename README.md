# Realtime Twitter Sentiment Analysis

Project for SFU's CMPT 732

Developer: Btara Truhandarien and Tommy Betz

# About

Realtime Twitter Sentiment Analysis, is a project bringing sentiment analysis of tweets on demand in realtime in the browser. It leverages [Twitter's streaming API](https://developer.twitter.com/en/docs/tutorials/consuming-streaming-data). The whole project itself is a streaming system and no intermediate data is stored. Select from a number of preselected topics with relatively high volume and you can see a live scatterplot of the rough sentiment of each tweet across time.

# On Giant's Shoulders
The system is possible with the help of these technologies built by giants:
1. [Python v3.6.7](https://www.python.org/) - As programming language of choice
2. [Docker](https://www.docker.com/) - As infrastructure orchestration and local development environment
3. [RabbitMq](https://www.rabbitmq.com/) - As a message passing solution
4. [Kafka](https://kafka.apache.org/) - To send the sentiment analysis to users
5. [Spark/PySpark](https://spark.apache.org/) - In order to accommodate for potential large scale distributed computation
6. [Tornado](http://www.tornadoweb.org/en/stable/) - As chosen web framework
7. [Celery](http://www.celeryproject.org/) - Distributed task queue

# Running
Please check [RUNNING.md](docs/RUNNING.md)

# Restrictions
The project is restricted in several ways:
1. It is not suited for full fledge production application, hence it assumes it will be run in a restricted environment e.g laptop/desktop where control is easy
2. It has been tested and built primarily on MacOS and Linux systems, Windows support is not guaranteed
3. It is not built with security in mind
4. The project is not meant to build a robust system for production usage (though still with some scalability in mind). Hence several things desired such as timeouts, disconnection handling, clearing resources etc. are not fully supported due to constraints