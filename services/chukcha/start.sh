#!/bin/bash

setarch `uname -m` -R /app/final/ -h 0.0.0.0 -p 1234 -d ./files
