# DGPTE Implementation with Commercial MLLMs

This module applies the DGPTE prompts to commercial MLLMs for performance testing and training-set annotation on Task1--Task3.

## Structure

```text
2_DGPTE_Implementation_with_Commercial_MLLMs/
├── configs/
│   ├── commercial_model.yaml
│   └── tasks.yaml
├── scripts/
│   ├── common.py
│   ├── dg_prompt.py
│   ├── qa_prompt.py
│   ├── performance_test.py
│   ├── automatic_annotation.py
│   └── calculate_accuracy.py
├── results/
│   ├── performance_testing/
│   ├── automatic_annotation/
│   └── accuracy/
├── .env.example
└── README.md
```

## Files

| File | Function |
|---|---|
| `configs/commercial_model.yaml` | Commercial model, image resolution, temperature, and retry settings. |
| `configs/tasks.yaml` | Data paths, grade labels, and required JSON fields for the three tasks. |
| `scripts/common.py` | Shared configuration, API, path, image, and JSON utilities. |
| `scripts/dg_prompt.py` | Builds performance-testing prompts 1--4. |
| `scripts/qa_prompt.py` | Builds the Prompt 4 annotation messages with ground truth and Q2. |
| `scripts/performance_test.py` | Calls the commercial model on the test images. |
| `scripts/automatic_annotation.py` | Generates model annotations for the training images. |
| `scripts/calculate_accuracy.py` | Calculates task- and prompt-specific accuracy from the saved test results. |

## Configuration

Model settings are stored in `configs/commercial_model.yaml`. API connection values are read from `.env`:

```text
COMMERCIAL_MLLM_API_KEY=
COMMERCIAL_MLLM_BASE_URL=
```

## Data

```text
Data/Sample_Dataset/<Task>/
1_Data_Processing/results/images/<Task>/
Prompt_Components/<Task>.py
```

## Run

```bash
python -m pip install openai PyYAML
```

Check a performance-testing prompt without an API request:

```bash
python scripts/performance_test.py --task Task1 --prompt 4 --limit 1 --dry-run
```

Run performance testing:

```bash
python scripts/performance_test.py --task Task1 --prompt 4
```

Run automatic annotation:

```bash
python scripts/automatic_annotation.py --task Task1
```

Calculate accuracy:

```bash
python scripts/calculate_accuracy.py --task Task1
python scripts/calculate_accuracy.py --task Task1 --prompt 4
```

## Results

```text
results/
├── performance_testing/<Task>/Prompt<1-4>/
│   ├── prompt.txt
│   └── <Model>/<test_image>.json
├── automatic_annotation/<Task>/
│   ├── prompt.txt
│   └── <Model>/<train_image>.json
└── accuracy/<Task>/
    └── Accuracy.csv
```

| Output | Content |
|---|---|
| `performance_testing/.../<test_image>.json` | Model response, predicted grade, true grade, and correctness. |
| `automatic_annotation/.../<train_image>.json` | Commercial-model annotation for one training image. |
| `Accuracy.csv` | Accuracy and sample counts for the available prompt/model results. |
