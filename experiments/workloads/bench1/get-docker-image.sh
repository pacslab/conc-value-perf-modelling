#! /bin/bash
echo "Usage: ./get-docker-image.sh \$SOCKETIO_SERVER"

GIT_SHA=$(git rev-parse --short HEAD)
DOCKER_IMAGE="ghcr.io/nimamahmoudi/conc-workloads-bench1:sha-${GIT_SHA:-latest}"
KNCOMMAND="kn service apply bench1 --image ${DOCKER_IMAGE} \\
            --env EXPERIMENT_NAME=TEST1 \\
            --env REPORT_INTERVAL=10 \\
            --env SOCKETIO_SERVER=${1:-http://172.17.0.1:3000}"

printf "\nDocker Image:\n\t${DOCKER_IMAGE}\n"

printf "\nKnative Command:\n\t${KNCOMMAND}\n\n"

