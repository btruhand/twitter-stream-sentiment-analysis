# Running the project

These are guidelines we give to run the project, in the order that needs to be done

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

This will spawn docker containers in the background. You can check the running containers by doing
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

### Rebuilding images
In the case that you have changed the source code or Dockerfile of the services and want to run your changes, then please do the following
```bash
cd /root/directory/of/project
docker-compose up -d --build [service name]
```
Where `[service name]` (without the square brackets) is the service that you have updated. The command above will recreate the running docker containers
with the latest changes

See: [what are Docker services](https://docs.docker.com/compose/compose-file/compose-file-v2/#service-configuration-reference))

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

## Troubleshooting
Here are some troubleshooting guidelines

### Docker requires login
You may encounter [this issue](https://github.com/docker/hub-feedback/issues/1103). If so the easiest way is for you to create an account
at [DockerHub](https://hub.docker.com/) and do a `docker login`