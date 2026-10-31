#!/bin/bash

# Run from the LLaMA-Factory root directory after exporting the model.
cd output/Multi-Task_Fine-tuned_MLLM
ollama create paper_gllm_joint_language_p1280_e300:latest -f Modelfile
ollama list
