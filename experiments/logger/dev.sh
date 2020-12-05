#!/bin/bash

# load environment variables
# export $(cat .env.dev | grep ^[A-Z] | xargs)

docker-compose -f docker-compose-dev.yml up --build

docker-compose -f docker-compose-dev.yml down

