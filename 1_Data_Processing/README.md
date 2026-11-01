# Data Processing

This module generates resolution-specific image copies for all three tasks while preserving the original aspect ratio. Images smaller than a requested resolution are copied without enlargement.

## Structure

```text
1_Data_Processing/
├── configs/
│   └── image_preprocessing.yaml
├── scripts/
│   └── resize_images.py
├── results/
│   └── images/
└── README.md
```

## Setup

```bash
python -m pip install Pillow PyYAML
```

The input dataset, result directory, and target resolutions are configured in `configs/image_preprocessing.yaml`. The default resolutions are 224, 448, 768, and 1280 pixels.

## Run

```bash
python scripts/resize_images.py
```

Generated images are written to both locations:

```text
Data/Sample_Dataset/
1_Data_Processing/results/images/
```

`Data/Sample_Dataset` contains only original images and annotation JSON files. All generated images are written to `1_Data_Processing/results/images`, which preserves the Task1–Task3 dataset hierarchy. A resolution suffix is appended to each generated filename, for example `test_Else_944_p1280.jpg`.
