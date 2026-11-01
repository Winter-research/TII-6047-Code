# Data

## Directory Layout

```text
Data/
├── README.md
├── Expert_Standards/
│   ├── Task1.txt
│   ├── Task2.txt
│   └── Task3.txt
├── Sample_Dataset/
│   ├── Task1/
│   │   ├── Reference_dataset/
│   │   ├── Train_dataset/
│   │   └── Test_dataset/
│   ├── Task2/
│   │   ├── Reference_dataset/
│   │   ├── Train_dataset/
│   │   └── Test_dataset/
│   └── Task3/
│       ├── Reference_dataset/
│       ├── Train_dataset/
│       └── Test_dataset/
└── Fine-Tuning_Dataset/
    ├── Task1_Fine-Tuning_Dataset.json
    ├── Task2_Fine-Tuning_Dataset.json
    ├── Task3_Fine-Tuning_Dataset.json
    └── Multi-Task_Fine-Tuning_Dataset.json
```

## Expert Standards

`Expert_Standards` records the grading rules for the three tasks:

| File | Task |
|---|---|
| `Task1.txt` | Tension-clamp crimping |
| `Task2.txt` | Guying-fitting corrosion |
| `Task3.txt` | Tangent-tower bird nest |

## Sample Dataset

Each image in `Sample_Dataset` has an annotation JSON file with the same filename stem.

| Directory | Use |
|---|---|
| `Reference_dataset` | Reference images and expert answers used in prompts |
| `Train_dataset` | Training images and annotations used to construct the fine-tuning datasets |
| `Test_dataset` | Test images and annotations used for performance evaluation |

The task labels are:

| Task | Grades |
|---|---|
| `Task1` | Else, Kind |
| `Task2` | Else, Kind, Major |
| `Task3` | Else, Kind, Major, Urgent |

Only the original images are stored in `Sample_Dataset`. Images resized by `1_Data_Processing/scripts/resize_images.py` are written to `1_Data_Processing/results/images`.

## Fine-Tuning Dataset

Run the following command from the repository root:

```bash
python 3_Fine-Tuning_Dataset_Construction/scripts/construct_dataset.py
```

The script writes the three single-task datasets and the combined multi-task dataset to `Fine-Tuning_Dataset`.
