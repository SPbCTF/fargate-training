#!/bin/bash
# Combine to one folder for easy deploy to /home/<service_name>

set -xe

mkdir -p deploy

cp -r services/chukcha deploy
cp -r services/cryptostorm deploy
cp -r services/haveibeenpwned deploy
cp -r services/imsorry deploy
cp -r services/kv8/service deploy/kv8
cp -r services/pokupaika deploy