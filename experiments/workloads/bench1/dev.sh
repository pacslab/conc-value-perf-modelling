#! /bin/bash

# start the container
docker-compose -f docker-compose-dev.yml up --build -d
# run bash
docker-compose -f docker-compose-dev.yml exec worker bash
# tear everything down
docker-compose -f docker-compose-dev.yml down -v
