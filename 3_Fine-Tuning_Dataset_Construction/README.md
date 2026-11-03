# Fine-Tuning Dataset Construction

This module converts the Prompt 4 components, reference examples, and annotated training samples into LLaMA-Factory multimodal datasets.

## Structure

```text
3_Fine-Tuning_Dataset_Construction/
├── configs/
│   └── dataset_construction.yaml
├── scripts/
│   └── construct_dataset.py
├── results/
│   ├── Task1_Fine-Tuning_Dataset.json
│   ├── Task2_Fine-Tuning_Dataset.json
│   ├── Task3_Fine-Tuning_Dataset.json
│   └── Multi-Task_Fine-Tuning_Dataset.json
└── README.md
```

## Files

| File | Function |
|---|---|
| `configs/dataset_construction.yaml` | Resolution, random seed, input directories, output directories, and output names. |
| `scripts/construct_dataset.py` | Builds the task-specific datasets and combines them into one multi-task dataset. |

## Configuration

```yaml
resolution: 1280
random_seed: 6047
sample_dataset_dir: Data/Sample_Dataset
processed_images_dir: 1_Data_Processing/results/images
```

The output directories and task filenames are set in the same YAML file.

## Data

```text
Data/Sample_Dataset/<Task>/
├── Reference_dataset/*.json
└── Train_dataset/*.json

1_Data_Processing/results/images/<Task>/
├── Reference_dataset/*_p1280.jpg
└── Train_dataset/*_p1280.jpg

Prompt_Components/<Task>.py
```

## Run

```bash
python -m pip install PyYAML
python scripts/construct_dataset.py
```

## Results

```text
results/
├── Task1_Fine-Tuning_Dataset.json
├── Task2_Fine-Tuning_Dataset.json
├── Task3_Fine-Tuning_Dataset.json
└── Multi-Task_Fine-Tuning_Dataset.json
```

The same four files are also written to:

```text
Data/Fine-Tuning_Dataset/
```

Each record contains a system message, a user Prompt 4 message, an assistant JSON answer, and the associated reference and training-image paths.
