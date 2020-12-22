#! /bin/bash

if [ -z "$1" ]
then
    echo "please pass a conc test name"
    exit 1
fi

# load environment variables
export $(cat .env.dev | grep ^[A-Z] | xargs)

# Home directory
export HOME_DIR=${HOME_DIR:-$(pwd)}

# start the container
docker-compose -f docker-compose-dev.yml up --build -d
# run test
docker-compose -f docker-compose-dev.yml exec --user root worker python conc_tester.py $1

curl --upload-file "src/conc_results/res_$1.csv" https://free.keep.sh