#! /bin/bash

curl --header "Content-Type: application/json" --request POST http://localhost:8080 --data '{"cmds":{"cpu":{"n":10000},"io":{"cnt":5,"rd":3,"size":"1M"},"run":{"cmd":"ls"},"sleep":0,"sleep_till":0,"stat":{"argv":1}}}'
# curl --header "Content-Type: application/json" --request POST http://localhost:8080 --data @test_params.json
