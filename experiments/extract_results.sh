#! /bin/bash

rm exp_results_figs.zip

# zip -r exp_results_figs.zip figs/* results/*
zip -r exp_results_figs.zip figs/*

# automatic upload makes it easier to transfer files
curl --upload-file ./exp_results_figs.zip https://free.keep.sh
