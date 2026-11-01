# Prompt Components Library

This package is the single source of truth for the task-specific prompt components used by commercial-model testing, automatic annotation, fine-tuning dataset construction, and fine-tuned-model verification.

## Structure

```text
Prompt_Components/
├── __init__.py
├── Task1.py
├── Task2.py
├── Task3.py
├── README.md
└── README_zh.md
```

Each task module defines the paper-aligned components:

```text
P_R                 Role prompt
P_T                 Task prompt
P_DT                graded decision tree
P_F                 output format
P_RI                reference-image introduction
P_RI_RESULT_ONLY    result-only reference introduction
P_OI                objective-image prompt
P_Q1_1 ... P_Q1_4   performance-testing questions
P_GR                ground-truth prompt
P_Q2                automatic-annotation question
```

## Import

```python
from Prompt_Components import load_components

prompts = load_components("Task1")
role_prompt = prompts["role"]
question_prompt = prompts["question_4"]
```

Reference images and their answers are not hard-coded in this package. Calling scripts load expert JSON files from `Data/Sample_Dataset`, load processed images from `1_Data_Processing/results/images`, and insert them into the message sequence at runtime.
