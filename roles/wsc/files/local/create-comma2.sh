#!/bin/bash

rm -f comma2.csv
n=$(cat inventory/wins.csv | wc -l)
for (( c=1; c<=n; c++)) ; do echo ",">> inventory/comma2.csv ; done

