#! /bin/bash

rm tmp.zip
zip tmp.zip results/*
# automatic upload makes it easier to transfer files
curl --upload-file ./tmp.zip https://free.keep.sh
