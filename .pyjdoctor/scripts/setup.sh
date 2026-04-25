#!/usr/bin/env bash
set -euo pipefail

# ----------------------------
# Config
# ----------------------------

echo "Building Docker Container"
pwd
#--no-cache 
#--build-arg CACHEBUST=$(date +%s)
docker build --build-arg CACHEBUST=$(date +%s) -f ./dockerfile-jdoctor --platform=linux/amd64 -t pjkroker/toradocu-3.0-x86 .