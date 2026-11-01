#!/bin/bash

# Run from the LLaMA-Factory root directory after exporting the model.
cd output/Multi-Task_Fine-tuned_MLLM
ollama create Task_Fine-tuned_MLLM -f Modelfile
ollama list
