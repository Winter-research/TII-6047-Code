Dear Editor and Reviewers,

Thank you for giving the author team the opportunity to revise and resubmit this manuscript. This repository provides the complete code and a limited amount of sample data used in the study. We hope that these materials can help the reviewers further understand and assess our work.

The Author Team

---

# Lightweight Multimodal LLM-Enabled Cost-Effective Defect Grading of Power Transmission Equipment in Power Grids (TII-26-6047)

This repository covers three defect-grading tasks:

| Task | Defect | Grades |
|---|---|---|
| `Task1` | Tension-clamp crimping | Else, Kind |
| `Task2` | Guying-fitting corrosion | Else, Kind, Major |
| `Task3` | Tangent-tower bird nest | Else, Kind, Major, Urgent |

## Execution Order

Run the modules in the following order:

```text
1. Process the images
       ↓
2. Test the commercial MLLM and generate automatic annotations
       ↓
3. Build the LLaMA-Factory fine-tuning datasets
       ↓
4. Fine-tune, export, and deploy the model
       ↓
5. Test the fine-tuned model and calculate the metrics
```

Run all commands from the `TII-6047-Code` repository root unless stated otherwise.

## 1. Process the Images

Install the dependencies:

```bash
python -m pip install Pillow PyYAML
```

Run:

```bash
python 1_Data_Processing/scripts/resize_images.py
```

The script reads the original images from:

```text
Data/Sample_Dataset/
```

Processed images are saved to:

```text
1_Data_Processing/results/images/
```

Set the required resolutions in `1_Data_Processing/configs/image_preprocessing.yaml`. The defaults are 224, 448, 768, and 1280.

## 2. Test the Commercial MLLM

Install the dependencies:

```bash
python -m pip install openai PyYAML
```

Copy the environment template:

```powershell
Copy-Item 2_DGPTE_Implementation_with_Commercial_MLLMs/.env.example `
  2_DGPTE_Implementation_with_Commercial_MLLMs/.env
```

Open `.env` and enter the commercial-model API key and base URL.

### 2.1 Run Performance Testing

```bash
python 2_DGPTE_Implementation_with_Commercial_MLLMs/scripts/performance_test.py --task Task1 --prompt 4
```

Set `--prompt` to `1`, `2`, `3`, or `4`. Replace `Task1` with `Task2` or `Task3` when testing another task.

The script saves the model responses in the corresponding result directory and records the complete prompt used for inference in `prompt.txt`.

### 2.2 Annotate the Training Images

```bash
python 2_DGPTE_Implementation_with_Commercial_MLLMs/scripts/automatic_annotation.py --task Task1
```

### 2.3 Calculate Accuracy

```bash
python 2_DGPTE_Implementation_with_Commercial_MLLMs/scripts/calculate_accuracy.py --task Task1 --prompt 4
```

Outputs are saved under:

```text
2_DGPTE_Implementation_with_Commercial_MLLMs/results/
├── performance_testing/
├── automatic_annotation/
└── accuracy/
```

Set the commercial model and image resolution in `2_DGPTE_Implementation_with_Commercial_MLLMs/configs/commercial_model.yaml`.

## 3. Build the Fine-Tuning Datasets

This script reads the 1280-pixel images generated in Step 1. Before running it, confirm that the required files are present in `1_Data_Processing/results/images`.

Run:

```bash
python 3_Fine-Tuning_Dataset_Construction/scripts/construct_dataset.py
```

The script generates:

```text
Task1_Fine-Tuning_Dataset.json
Task2_Fine-Tuning_Dataset.json
Task3_Fine-Tuning_Dataset.json
Multi-Task_Fine-Tuning_Dataset.json
```

The files are saved in both:

```text
Data/Fine-Tuning_Dataset/
3_Fine-Tuning_Dataset_Construction/results/
```

## 4. Fine-Tune and Deploy the Model

Install LLaMA-Factory and Ollama on the server. Copy the training and export configurations into LLaMA-Factory:

```bash
cp /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/configs/training/Multi-Task_Fine-tuned_MLLM.yaml examples/train_lora/
cp /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/configs/export/Multi-Task_Fine-tuned_MLLM.yaml examples/merge_lora/
```

Register `Multi-Task_Fine-Tuning_Dataset.json` in LLaMA-Factory's `data/dataset_info.json`. The registration name must match the `dataset` field in the training YAML.

Run the following commands from the LLaMA-Factory root directory:

```bash
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/01_train_lora.sh
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/02_export_model.sh
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/03_create_ollama_model.sh
```

The default deployed Ollama model is:

```text
paper_gllm_joint_language_p1280_e300:latest
```

## 5. Test the Fine-Tuned Model

Install the dependencies and start Ollama:

```bash
python -m pip install requests PyYAML openai
```

Set the Ollama URL and model name in:

```text
5_Performance_Verification_of_the_Fine-Tuned_MLLM/configs/ollama_model.yaml
```

### 5.1 Run Inference

Run all three tasks:

```bash
python 5_Performance_Verification_of_the_Fine-Tuned_MLLM/scripts/performance_test.py
```

Run only Task1:

```bash
python 5_Performance_Verification_of_the_Fine-Tuned_MLLM/scripts/performance_test.py --tasks Task1
```

Inference results are saved by task under `5_Performance_Verification_of_the_Fine-Tuned_MLLM/results`.

### 5.2 Calculate the Metrics

Calculate the grading and CoT metrics for Task1:

```bash
python 5_Performance_Verification_of_the_Fine-Tuned_MLLM/scripts/calculate_metrics.py --task Task1
```

To calculate only grading metrics such as ACC, MP, MR, MF1, and NMAE, run:

```bash
python 5_Performance_Verification_of_the_Fine-Tuned_MLLM/scripts/calculate_metrics.py --task Task1 --skip-cot-api
```

This option skips commercial-model-based CoT evaluation and does not calculate visual correctness, logical correctness, fully correct rate, or hallucination rates.

Replace `Task1` with `Task2` or `Task3` to calculate a different task independently.

## Shared Directories

| Directory | Use |
|---|---|
| `Data` | Expert standards, original sample data, and generated fine-tuning datasets |
| `Prompt_Components` | Shared English prompt components for Task1–Task3 |
| `Metrics` | Grading-performance and CoT-reliability metric functions |

## Detailed Documentation

| Module | Documentation |
|---|---|
| 1_Data_Processing | [README](1_Data_Processing/README.md) |
| 2_DGPTE_Implementation_with_Commercial_MLLMs | [README](2_DGPTE_Implementation_with_Commercial_MLLMs/README.md) |
| 3_Fine-Tuning_Dataset_Construction | [README](3_Fine-Tuning_Dataset_Construction/README.md) |
| 4_MLLM_Fine-Tuning_and_Local_Deployment | [README](4_MLLM_Fine-Tuning_and_Local_Deployment/README.md) |
| 5_Performance_Verification_of_the_Fine-Tuned_MLLM | [README](5_Performance_Verification_of_the_Fine-Tuned_MLLM/README.md) |
| Data | [README](Data/README.md) |
| Prompt components | [README](Prompt_Components/README.md) |
| Metrics | [README](Metrics/README.md) |
