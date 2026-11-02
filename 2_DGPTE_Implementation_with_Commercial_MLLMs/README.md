# DGPTE Implementation with Commercial MLLMs

[Chinese version](README_zh.md)

This module implements commercial-MLLM performance testing and automatic annotation for Task1, Task2, and Task3. It also calculates classification accuracy for the commercial-model outputs.

## Structure

```text
2_DGPTE_Implementation_with_Commercial_MLLMs/
├── configs/
│   ├── commercial_model.yaml
│   └── tasks.yaml
├── scripts/
│   ├── dg_prompt.py
│   ├── qa_prompt.py
│   ├── performance_test.py
│   ├── automatic_annotation.py
│   ├── calculate_accuracy.py
│   └── common.py
├── results/
│   ├── performance_testing/
│   ├── automatic_annotation/
│   └── accuracy/
├── .env.example
└── README.md
```

Prompt components are imported from the repository-level `Prompt_Components` package. Expert JSON files are loaded from `Data/Sample_Dataset`, while resolution-specific images are loaded from `1_Data_Processing/results/images`.

## Setup

```bash
python -m pip install openai PyYAML
```

Create the local API configuration:

```powershell
Copy-Item .env.example .env
```

```text
COMMERCIAL_MLLM_API_KEY=your-api-key
COMMERCIAL_MLLM_BASE_URL=https://your-api-endpoint/v1
```

Model and request parameters are defined in `configs/commercial_model.yaml`. Task labels, expected JSON fields, and dataset paths are defined in `configs/tasks.yaml`.

## Performance Testing

```bash
python scripts/performance_test.py --task Task1 --prompt 4
```

`--task` accepts `Task1`, `Task2`, or `Task3`; `--prompt` accepts `1`, `2`, `3`, or `4`.

## Automatic Annotation

```bash
python scripts/automatic_annotation.py --task Task1
```

## Accuracy

```bash
python scripts/calculate_accuracy.py --task Task1
```
