#!/bin/bash

# ------ Task1 pilot test ------
# ------ Task1.1 qwen2.5:72b pilot ------
MODEL="qwen2.5:72b"  
RESULTS_DIR="res/pilot/genehop/qwen2.5_72b"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR

# eutils
MASK="101110"
INPUT_FILE="data/genehop101110-10Qs.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

# blast
MASK="111011"
INPUT_FILE="data/genehop111011-10Qs.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task1.1 qwen2.5:72b-pilot completed."


# ------ Task2 optimized test ------
# ------ Task2.1 qwen2.5:32b optimized ------
MODEL="qwen2.5:32b"  
RESULTS_DIR="res/optimzed/genehop/qwen2.5_32b"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR

# eutils
MASK="101110"
INPUT_FILE="data/genehop101110.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

# blast
MASK="111011"
INPUT_FILE="data/genehop111011.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task2.1 qwen2.5:32b-optimized completed."


# ------ Task2.2 qwen2.5:72b optimized ------
MODEL="qwen2.5:72b"  
RESULTS_DIR="res/optimzed/genehop/qwen2.5_72b"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR

# eutils
MASK="101110"
INPUT_FILE="data/genehop101110.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

# blast
MASK="111011"
INPUT_FILE="data/genehop111011.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task2.2 qwen2.5:72b-optimized completed."


# ------ Task2.3 qwen2.5:32b multi-step reasoning ------
MODEL="qwen2.5:32b"  
RESULTS_DIR="res/optimzed/genehop/qwen2.5_32b-reasoning"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR

# eutils
MASK="1011101"
INPUT_FILE="data/disease_gene_location-error.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task2.3 qwen2.5:32b-reasoning-optimized completed."


# ------ Task2.4 qwen2.5:72b multi-step reasoning ------
MODEL="qwen2.5:72b"  
RESULTS_DIR="res/optimzed/genehop/qwen2.5_72b-reasoning"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR

# eutils
MASK="1011101"
INPUT_FILE="data/disease_gene_location-error.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task2.4 qwen2.5:72b-reasoning-optimized completed."


# Complete all tasks
echo "All GeneHop tasks completed."
