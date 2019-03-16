#!/bin/bash
# Copy files to vulnbox and run everything

set -xe

usage(){
    echo "$0 ip"
}


if [ -z "$1" ]; then
    echo "Should specify ip address"
    usage
    exit
fi

if ! [ -e "./deploy" ]; then
    echo "Should run combine.sh first"
fi

scp -r deploy "root@$1:/home"
ssh "root@$ip" cd /home && bash -c "for s in $(ls); do cd \$s && docker-compose up -d && cd -; done"