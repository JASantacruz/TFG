#!/bin/bash

# Create docker host
#export DOCKER_HOST=unix:///var/run/docker.sock
# Run docker machine
#FIRST_CONTAINER=$(docker ps -q | awk 'NR==1{print $1}')
#docker start ${FIRST_CONTAINER}

echo "Accessing to environment..."
source env/bin/activate

echo "Starting server..."
python3 server.py > server.log 2>&1 &

if [ $? -ne 0 ]; then
    echo "Error starting server"
    exit 1
fi

echo "Server started!"
echo "Starting Ngrok..."
ngrok http --domain=tfg.ngrok.dev 8080 > ngrok.log 2>&1 &
if [ $? -ne 0 ]; then
    echo "Error starting ngrok"
    exit 1
fi
