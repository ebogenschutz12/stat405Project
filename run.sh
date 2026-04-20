#!/bin/bash

file=$1

echo "Running analysis on: $file"

Rscript helpfulness_fast.R $file
