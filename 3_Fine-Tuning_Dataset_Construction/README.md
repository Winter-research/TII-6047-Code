# Fine-Tuning Dataset Construction

This module converts the expert-annotated training data, reference examples, and Prompt 4 components into LLaMA-Factory-compatible multimodal fine-tuning datasets.

## Structure

```text
3_Fine-Tuning_Dataset_Construction/
├── configs/
│   └── dataset_construction.yaml
├── scripts/
│   └── construct_dataset.py
├── results/
└── README.md
```

## Setup

```bash
python -m pip install PyYAML
```

The script reads expert JSON data from `Data/Sample_Dataset`, imports Prompt 4 components from `Prompt_Components`, and uses `_p1280.jpg` images from `1_Data_Processing/results/images` by default.

## Run

```bash
python scripts/construct_dataset.py
```

The generated files are written to both:

```text
Data/Fine-Tuning_Dataset/
3_Fine-Tuning_Dataset_Construction/results/
```

Outputs:

```text
Task1_Fine-Tuning_Dataset.json
Task2_Fine-Tuning_Dataset.json
Task3_Fine-Tuning_Dataset.json
Multi-Task_Fine-Tuning_Dataset.json
```
