#!/bin/bash

docker container stop filebenchExp
docker container rm filebenchExp
#memory --memory
docker run --cpus=$1 --cpuset-cpus="0-1" --memory=$2 --name=filebenchExp --privileged  -v /tmp:/home/ -dit modified_filebench 
#docker exec -it filebenchExp /bin/bash
cp  $3 /tmp
docker exec -it filebenchExp filebench -f /home/$3

