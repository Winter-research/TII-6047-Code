# MLLM Fine-Tuning and Local Deployment

[中文说明](README_zh.md)

This module provides the LLaMA-Factory configurations and execution scripts used to fine-tune, merge, export, and locally deploy the multi-task MLLM.

## Structure

```text
4_MLLM_Fine-Tuning_and_Local_Deployment/
├── configs/
│   ├── training/
│   │   └── Multi-Task_Fine-tuned_MLLM.yaml
│   └── export/
│       └── Multi-Task_Fine-tuned_MLLM.yaml
├── scripts/
│   ├── 01_train_lora.sh
│   ├── 02_check_training.sh
│   ├── 03_export_model.sh
│   └── 04_create_ollama_model.sh
├── results/
│   └── Exported_Model_Files.txt
├── README.md
└── README_zh.md
```

## Requirements

- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)
- [Ollama](https://github.com/ollama/ollama)

Run the scripts from the LLaMA-Factory root directory. First copy the configurations into LLaMA-Factory:

```bash
cp /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/configs/training/Multi-Task_Fine-tuned_MLLM.yaml examples/train_lora/
cp /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/configs/export/Multi-Task_Fine-tuned_MLLM.yaml examples/merge_lora/
```

Register `Multi-Task_Fine-Tuning_Dataset.json` in `data/dataset_info.json`. The registration name must match the `dataset` field in the training YAML.

## Run

```bash
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/01_train_lora.sh
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/02_check_training.sh
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/03_export_model.sh
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/04_create_ollama_model.sh
```

The deployed Ollama model name is `paper_gllm_joint_language_p1280_e300:latest`. Model weights are not included in this repository. The expected exported-file list is recorded in `results/Exported_Model_Files.txt`.

