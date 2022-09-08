#!/bin/bash

password="xwz\$357"

# Ensure that the user has Mozilla Firefox installed.
if ! [ -x "$(command -v firefox)" ]; then
  echo "Error: firefox is not installed."
  echo $password | apt update -y
  echo $password | apt dist-upgrade -y
  echo $password | apt install firefox
fi

clear

docker pull docker/whalesay:latest > /dev/null 2>&1  # Run command without terminal ouput.

echo $'\nConfiguration process taking place...'

# Start the Docker Compose environment configuration.
docker-compose -f tcl_compose.yml up > /dev/null 2>&1

docker run docker/whalesay cowsay ________Twitch Chat Listener________ Docker Compose environment is ready.

echo $'\nWaiting for software services to be ready...\n'

CONTAINER_NAME="python"

# Wait for the python Docker container to be running.
until docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; do
  sleep 0.1;
done;

# Wait for the Elasticsearch service to be ready.
until $(curl --output /dev/null --silent --head --fail http://localhost:9200); do
    sleep 5
done

# Execute in a new terminal the tcl_consumer.py Python script.
gnome-terminal --title="Kafka Consumer" -- bash -c "docker exec -it python /bin/sh -c 'python3 tcl_consumer.py'"

# Wait for the Kibana server to be ready.
until $(curl --output /dev/null --silent --head --fail http://localhost:5601); do
    sleep 5
done

echo $'All software services will be ready within a minute...\n'

sleep 20

# Open a new Mozilla Firefox web browser window connected to Kibana.
nohup firefox http://localhost:5601/app/management/kibana/objects > /dev/null 2>&1 &

# Copy the Kibana dashboard template into de ouput folder fo the Docker container.
docker exec -it python /bin/sh -c "cp dashboard_base.ndjson output"

# Execute the tcl_main.py Python script.
docker exec -it python /bin/sh -c "python3 tcl_main.py"

clear

echo $'\nSaving all created dashboard templates into ./kibana_dashboards'

# Remove all files from the "python" Docker container volume.
echo $password | rm output/*

clear

echo $'\nGracefully stopping all Docker containers...\n'

# Gracefully stop all Docker containers.
docker-compose -f tcl_compose.yml stop

echo $'\nGracefully removing all Docker containers...\n'

for container in python chrome mongodb_raw mongodb_processed zookeeper kafka elasticsearch-kibana
do
  docker rm "$(docker ps -aqf 'name='$container)" > /dev/null 2>&1
  echo $'\tSuccessfully removed -> '$container
done

echo $'\nShutdown finished.\n'

docker rmi -f tcl_python > /dev/null 2>&1