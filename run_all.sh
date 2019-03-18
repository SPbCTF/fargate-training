#!/bin/bash
# Run everything

set -xe

cd /home
for service in $(ls)
do 
    cd $service
    docker-compose up -d
    cd -
done