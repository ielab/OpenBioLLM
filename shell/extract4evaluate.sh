#!/bin/bash

# input folder 
INPUT_FILE="res"
echo "Extracting ground truth and answer INPUT_FILE=$INPUT_FILE"

python -u extract4evaluate.py \
    --input-dir "$INPUT_FILE" \

echo "Extracting $INPUT_FILE completed."



