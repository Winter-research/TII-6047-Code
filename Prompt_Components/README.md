# Prompt Components

This package stores the prompt components shared by commercial-model testing, automatic annotation, fine-tuning dataset construction, and fine-tuned-model verification.

## Structure

```text
Prompt_Components/
├── __init__.py
├── Task1.py
├── Task2.py
├── Task3.py
└── README.md
```

## Files

| File | Function |
|---|---|
| `__init__.py` | Validates the task name and returns a copy of its component dictionary. |
| `Task1.py` | Tension-clamp crimping prompts and decision tree. |
| `Task2.py` | Guying-fitting corrosion prompts and decision tree. |
| `Task3.py` | Tangent-tower bird-nest prompts and decision tree. |

## Components

| Constant | Content |
|---|---|
| `P_R` | Role prompt. |
| `P_T` | Task definition. |
| `P_DT` | Grading decision tree. |
| `P_F` | JSON output format. |
| `P_RI` | Reference-image introduction for CoT prompts. |
| `P_RI_RESULT_ONLY` | Reference-image introduction for result-only prompts. |
| `P_OI`, `P_OI_INSTRUCTION` | Objective-image prompt and instruction. |
| `P_Q1_1`--`P_Q1_4` | Performance-testing questions for Prompt 1--4. |
| `P_GR` | Ground-truth grade used in automatic annotation. |
| `P_Q2` | Automatic-annotation question. |

## Data

Reference answers are read from the expert-reviewed JSON files in `Data/Sample_Dataset`. Reference and objective images are loaded from `1_Data_Processing/results/images` by the calling script.

## Import Interface

```python
from Prompt_Components import load_components

prompts = load_components("Task1")
role_prompt = prompts["role"]
question_prompt = prompts["question_4"]
```
