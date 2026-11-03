# MLLM Fine-Tuning and Local Deployment

This module contains the LLaMA-Factory configurations and shell scripts for LoRA fine-tuning, model export, and Ollama deployment.

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
│   ├── 02_export_model.sh
│   └── 03_create_ollama_model.sh
├── results/
│   └── Exported_Model_Files.txt
└── README.md
```

## Files

| File | Function |
|---|---|
| `configs/training/Multi-Task_Fine-tuned_MLLM.yaml` | Qwen3-VL LoRA training, dataset, output, and optimization settings. |
| `configs/export/Multi-Task_Fine-tuned_MLLM.yaml` | LoRA checkpoint merge and model export settings. |
| `scripts/01_train_lora.sh` | Starts LLaMA-Factory LoRA training. |
| `scripts/02_export_model.sh` | Merges the selected checkpoint and exports the full model. |
| `scripts/03_create_ollama_model.sh` | Creates the Ollama model from the exported `Modelfile`. |
| `results/Exported_Model_Files.txt` | Expected files in the exported model directory. |

## Configuration

The training configuration uses:

```text
Base model: Qwen/Qwen3-VL-8B-Instruct
Dataset: Multi-Task_Fine-Tuning_Dataset
Fine-tuning method: LoRA
Output: saves/Qwen3-VL-8B-Instruct/lora/Multi-Task_Fine-tuned_MLLM
```

Set the checkpoint used by `adapter_name_or_path` in the export YAML before exporting.

## Data

Copy the constructed dataset into the LLaMA-Factory `data/` directory and register it in `data/dataset_info.json` as:

```text
Multi-Task_Fine-Tuning_Dataset
```

The registration name must match the `dataset` value in the training YAML.

## Run

Requirements:

- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)
- [Ollama](https://github.com/ollama/ollama)

Set `TII_CODE_ROOT` to the repository root. From the LLaMA-Factory root directory, copy the configurations:

```bash
cp "$TII_CODE_ROOT/4_MLLM_Fine-Tuning_and_Local_Deployment/configs/training/Multi-Task_Fine-tuned_MLLM.yaml" examples/train_lora/
cp "$TII_CODE_ROOT/4_MLLM_Fine-Tuning_and_Local_Deployment/configs/export/Multi-Task_Fine-tuned_MLLM.yaml" examples/merge_lora/
```

Run training, export, and deployment in order:

```bash
bash "$TII_CODE_ROOT/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/01_train_lora.sh"
bash "$TII_CODE_ROOT/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/02_export_model.sh"
bash "$TII_CODE_ROOT/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/03_create_ollama_model.sh"
```

## Results

The exported model is written by LLaMA-Factory to:

```text
output/Multi-Task_Fine-tuned_MLLM/
```

Model weights are not stored in this repository. `results/Exported_Model_Files.txt` records the expected exported files. The Ollama script registers the model as `Task_Fine-tuned_MLLM`.

