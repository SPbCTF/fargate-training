#!/bin/bash

echo 0 > /proc/sys/kernel/randomize_va_space

setarch i386 -R /app/final

exec /app/final -h 0.0.0.0 -p 1234 -d ./files