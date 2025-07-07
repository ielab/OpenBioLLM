#!/bin/bash

# ------ Task1 pilot test ------
# ------ Task1.1 llama3.1 pilot ------
MODEL="llama3.1:70b"
RESULTS_DIR="res/pilot/geneturing/llama3.1_70b"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR
MASK="111111"
INPUT_FILE="data/geneturing-10Qs.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task1.1 llama3.1 pilot completed."


# ------ Task1.2 qwen2.5 pilot ------
MODEL="qwen2.5:72b"
RESULTS_DIR="res/pilot/geneturing/qwen2.5_72b"
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR
MASK="111111"
INPUT_FILE="data/geneturing-10Qs.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task1.2 qwen2.5 pilot completed."


# ------ Task1.3 qwen2.5-coder pilot ------
MODEL="qwen2.5-coder:32b"
RESULTS_DIR="res/pilot/geneturing/qwen2.5-coder_32b"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR
MASK="111111"
INPUT_FILE="data/geneturing-10Qs.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task1.3 qwen2.5-coder pilot completed."



# ------ Task2 optimized full test ------
# ------ Task2.1 qwen2.5:32b-full optimized ------
MODEL="qwen2.5:32b"
RESULTS_DIR="res/optimzed/geneturing/-full/qwen2.5_32b"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR
MASK="111111"
INPUT_FILE="data/geneturing.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task2.1 qwen2.5:32b-full-optimized completed."


# ------ Task2.2 qwen2.5:72b-full optimized ------
MODEL="qwen2.5:72b"
RESULTS_DIR="res/optimzed/geneturing/-full/qwen2.5_72b"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR
MASK="111111"
INPUT_FILE="data/geneturing.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task2.2 qwen2.5:72b-full optimized completed."




# ------ Task3 optimized slim test ------
# ------ Task3.1 qwen2.5:32b -slim optimized ------
MODEL="qwen2.5:32b"
RESULTS_DIR="res/optimzed/geneturing/-slim/qwen2.5_32b"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR
MASK="001001"
INPUT_FILE="data/geneturing.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task3.1 qwen2.5:32b-slim-optimized completed."


# ------ Task3.2 qwen2.5:72b -slim optimized ------
MODEL="qwen2.5:72b"
RESULTS_DIR="res/optimzed/geneturing/-slim/qwen2.5_72b"   
CURRENT_TIME=$(date +"%Y-%m-%d_%H:%M:%S")
mkdir -p $RESULTS_DIR
MASK="001001"
INPUT_FILE="data/geneturing.json"
LOG_FILENAME="${RESULTS_DIR}/${MODEL}_${MASK}_${CURRENT_TIME}.log"

echo "Running Task using Model=$MODEL with MASK=$MASK and INPUT_FILE=$INPUT_FILE"
echo "Logging to $LOG_FILENAME"

python -u main.py \
    "$MASK" \
    --model "$MODEL" \
    --input "$INPUT_FILE" \
    --results-dir "$RESULTS_DIR" \
    --log-file "$LOG_FILENAME"

echo "Task3.2 qwen2.5:72b -slim-optimized completed."


# Complete all tasks
echo "All GeneTuring tasks completed."
