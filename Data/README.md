# Data

[中文说明](README_zh.md)

This directory contains the expert standards, executable sample data, and generated fine-tuning datasets required by the repository.

## Structure

```text
Data/
├── Expert_Standards/
│   ├── Task1.txt
│   ├── Task2.txt
│   └── Task3.txt
├── Sample_Dataset/
│   ├── Task1/
│   ├── Task2/
│   └── Task3/
└── Fine-Tuning_Dataset/
    ├── Task1_Fine-Tuning_Dataset.json
    ├── Task2_Fine-Tuning_Dataset.json
    ├── Task3_Fine-Tuning_Dataset.json
    └── Multi-Task_Fine-Tuning_Dataset.json
```

## Sample Dataset

Each task contains:

```text
TaskX/
├── Reference_dataset/
├── Train_dataset/
└── Test_dataset/
```

- `Reference_dataset` supplies expert-verified in-context examples.
- `Train_dataset` supplies images and annotations for fine-tuning dataset construction and automatic annotation.
- `Test_dataset` supplies held-out samples for performance verification.

`Sample_Dataset` contains only original images and same-stem annotation JSON files. Resolution-specific images are stored separately under `1_Data_Processing/results/images`.

## Tasks

- `Task1`: tension-clamp crimping assessment.
- `Task2`: guying-fitting corrosion assessment.
- `Task3`: tangent-tower bird-nest assessment.

The sample data are included to make the complete processing, prompt, fine-tuning, and evaluation workflows executable.
