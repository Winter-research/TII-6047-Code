#!/bin/bash

# Run from the LLaMA-Factory root directory.
OUTPUT_DIR="saves/Qwen3-VL-8B-Instruct/lora/Multi-Task_Fine-tuned_MLLM"

if [ -f "${OUTPUT_DIR}/train_results.json" ] || [ -f "${OUTPUT_DIR}/all_results.json" ]; then
  echo "Training status: COMPLETED"
else
  echo "Training status: NOT COMPLETED"
fi

find "${OUTPUT_DIR}" -maxdepth 1 -type d -name 'checkpoint-*' 2>/dev/null | sort -V
