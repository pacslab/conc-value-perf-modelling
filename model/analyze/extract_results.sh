#! /bin/bash

rm model_results_figs.zip

# zip -r model_results_figs.zip figs/* results/*
zip -r model_results_figs.zip figs/*

# automatic upload makes it easier to transfer files
curl --upload-file ./model_results_figs.zip https://free.keep.sh
