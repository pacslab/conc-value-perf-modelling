#! /bin/bash

# load environment variables
export $(cat .env.dev | grep ^[A-Z] | xargs)

# Home directory
export HOME_DIR=${HOME_DIR:-$(pwd)}

# start the container
docker-compose -f docker-compose-dev.yml up --build -d
# run bash
docker-compose -f docker-compose-dev.yml exec --user root worker bash
# tear everything down
docker-compose -f docker-compose-dev.yml down -v
