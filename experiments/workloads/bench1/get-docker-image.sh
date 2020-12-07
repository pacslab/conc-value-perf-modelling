#! /bin/bash
echo "Usage: ./get-docker-image.sh \$SOCKETIO_SERVER"

GIT_SHA=$(git rev-parse --short HEAD)
DOCKER_IMAGE="ghcr.io/nimamahmoudi/conc-workloads-bench1:sha-${GIT_SHA:-latest}"
KNCOMMAND="kn service apply bench1 --image ${DOCKER_IMAGE} \\
            --env EXPERIMENT_NAME=TEST1 \\
            --env REPORT_INTERVAL=10 \\
            --env SOCKETIO_SERVER=${1:-http://172.17.0.1:3000} \\
            --limit 'cpu=250m,memory=256Mi' \\
            --concurrency-limit 5 \\
            -a autoscaling.knative.dev/panicThresholdPercentage=1000 \\
            # --concurrency-target 5 \\
            # --concurrency-utilization 90 \\
            # --autoscale-window 60s \\
            # -a autoscaling.knative.dev/window=60s
            "

GCP_PROJECT_ID=${GCP_PROJECT_ID:-PROJECTID}
GCR_IMAGE="gcr.io/$GCP_PROJECT_ID/bench1:sha-$GIT_SHA"
GCPRUNCOMMAND="
        docker pull $DOCKER_IMAGE
        docker tag $DOCKER_IMAGE $GCR_IMAGE
        docker push $GCR_IMAGE

        # deploy
        gcloud run deploy --image $GCR_IMAGE --platform managed \\
            --concurrency=5 \\
            --memory=256Mi \\
            --set-env-vars=EXPERIMENT_NAME=TEST1,REPORT_INTERVAL=10,SOCKETIO_SERVER=${1:-http://172.17.0.1:3000} \\
            --region=us-central1 \\
            --max-instances=20

        # delete
        gcloud run services delete bench1
        # list container images
        gcloud container images list-tags gcr.io/$GCP_PROJECT_ID/bench1
        gcloud container images delete gcr.io/$GCP_PROJECT_ID/bench1:sha-$GIT_SHA
        # now you need to delete the s3 bucket automatically created
"

printf "\nDocker Image:\n\t${DOCKER_IMAGE}\n"
printf "\nKnative Command:\n\t${KNCOMMAND}\n\n"
printf "\nDocker Cloud Run:\n\t${GCPRUNCOMMAND}\n\n"

