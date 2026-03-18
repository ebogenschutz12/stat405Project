#!/bin/bash

file="amazon_reviews_us_Electronics_v1_00.tsv"

echo "Processing $file (first 10000 rows)"

head -n 10001 "$file" | awk -F '\t' '
NR > 1 {sum += $8; count++}
END {if (count > 0) print "Average rating:", sum/count}
'
