# Running the project

These are guidelines we give to run the project, in the order that needs to be done

## Getting Twitter consumer API keys and tokens
You would require getting a Twitter consumer API key and tokens. You can get them by applying for a [Twitter application
dev account](https://developer.twitter.com/content/developer-twitter/en.html)

After you get them please replace the placeholder in `config.json`

## Install Docker
We leverage Docker to run the project. If you haven't please download these components:
- [Docker for Mac](https://docs.docker.com/docker-for-mac/install/) if you are a Mac user
- [Docker for Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/) if you are a Ubuntu user
- [Docker Compose](https://docs.docker.com/compose/install/#install-compose) if you are a Ubuntu user

The above assumes you are either a Mac or Ubuntu user, please adjust as needed for your particular system.
Remember to do any Docker configuration for your system beforehand.

For ease, if possible run the project on Mac which covers most of the setup for you

## Building images
Individual Dockerfiles have been provided in `./docker/` if you wish to build images individually.
However the recommended approach is to do
```bash
cd /root/directory/of/project
docker-compose build
```

This way all the necessary images will be build and with the correct tags as required

## Running the project
You can easily run the project with the following command
```bash
cd /root/directory/of/project
docker-compose up -d
```

This will spawn docker containers in the background (give it several seconds). You can check the running containers by doing
```bash
docker container ls
```

To stop the project run
```bash
cd /root/directory/of/project
docker-compose down
```

### About the containers
In detail these are the containers that you should see:
1. A single container for the web application
2. Two RabbitMq containers
3. Two celery worker containers
4. A zookeeper container
5. Two kafka broker containers
6. Two celery task containers (they're named `streamer`)
7. A single Spark app container

### First time setup
If this is your first time running the containers then please also do the following after `docker-compose up -d`
```bash
./scripts/create-kafka-topics.sh
./scripts/create-kafka-sentiment-topics.sh
```
The command above will create the necessary kafka topics needed for the project

### Rebuilding images
In the case that you have changed the source code or Dockerfile of the services and want to run your changes, then please do the following
```bash
cd /root/directory/of/project
docker-compose up -d --build [service name]
```
Where `[service name]` (without the square brackets) is the service that you have updated. The command above will recreate the running docker containers
with the latest changes

See: [what are Docker services](https://docs.docker.com/compose/compose-file/compose-file-v2/#service-configuration-reference)

## Frontend view
Once you start the containers you can check the following in the browser:
1. `localhost` for the web application
2. `localhost:15672` for the RabbitMq management board

Please check on `localhost:15672` that there are 2 nodes in the cluster: `rabbit@rabbitmq1` and `rabbit@rabbitmq2`. The available user setup is `bigdata` with password `bigdata`.

## Seeing logs of containers
To see all the project's containers logs
```bash
cd /root/directory/of/project
docker-compose logs -f -t
```

If you want to see a particular service's logs then you can run
```bash
cd /root/directory/of/project
docker-compose logs -f -t [service name]
```
__Note__: You can specify more than one service name at a time

## Troubleshooting
Here are some troubleshooting guidelines

### Docker requires login
You may encounter [this issue](https://github.com/docker/hub-feedback/issues/1103). If so the easiest way is for you to create an account
at [DockerHub](https://hub.docker.com/) and do a `docker login`

### Docker port in use
Ports `80` and `15672` on the host (a.k.a your computer) is used to bind to some of the container's ports. If Docker says port `80` or `15672` is in use,
please check if any applications are using those ports and stop those applications first. Alternatively you can modify the port bindings in `docker-compose.yml`
under `streaming-web` and `rabbitmq` services.

### Kafka broker immediately went down because NodeExist/Kafka is unhealthy
Did you check `docker-compose logs kafka1 kafka2` and saw a log message like this:
```bash
[2018-12-04 21:51:19,463] ERROR [KafkaServer id=1] Fatal error during KafkaServer startup. Prepare to shutdown (kafka.server.KafkaServer)
org.apache.zookeeper.KeeperException$NodeExistsException: KeeperErrorCode = NodeExists
	at org.apache.zookeeper.KeeperException.create(KeeperException.java:119)
	at kafka.zk.KafkaZkClient.checkedEphemeralCreate(KafkaZkClient.scala:1485)
	at kafka.zk.KafkaZkClient.registerBrokerInZk(KafkaZkClient.scala:84)
	at kafka.server.KafkaServer.startup(KafkaServer.scala:257)
	at kafka.server.KafkaServerStartable.startup(KafkaServerStartable.scala:38)
	at kafka.Kafka$.main(Kafka.scala:75)
	at kafka.Kafka.main(Kafka.scala)
```

Or did you do `docker container ls` and saw Kafka containers are unhealthy or that you can't bring up a service because of Kafka being unhealthy?

Yes this is an unresolved issue that is raised in this [GitHub issue](https://github.com/bitnami/bitnami-docker-kafka/issues/33). This most likely
happened after you did a `docker-compose down` and tried to do `docker-compose up -d` again. The easiest solution would be to do:
```
docker-compose stop kafka1 kafka2
docker-compose up -d
```
Just repeat the process until it works, at least this is the workaround for now

### The project keeps getting stuck after some time
We don't know exactly why this happens... but we're guessing it is because of the heaviness of the Spark application. For [reference](https://github.com/docker/docker-py/issues/1374)
