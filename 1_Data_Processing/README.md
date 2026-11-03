# Data Processing

This module generates 224, 448, 768, and 1280-pixel image copies for Task1--Task3. The longest side is resized while the original aspect ratio is retained.

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

## Files

| File | Function |
|---|---|
| `configs/image_preprocessing.yaml` | Input directory, output directory, and target resolutions. |
| `scripts/resize_images.py` | Traverses all tasks and datasets, resizes supported images, and adds a resolution suffix. |

## Configuration

```yaml
dataset_dir: Data/Sample_Dataset
results_dir: 1_Data_Processing/results/images
resolutions: [224, 448, 768, 1280]
```

Images are not enlarged when their longest side is below the selected resolution.

## Data

Original images and annotation JSON files remain in:

```text
Data/Sample_Dataset/<Task>/<Dataset>/
```

## Run

```bash
python -m pip install Pillow PyYAML
python scripts/resize_images.py
```

Generate selected resolutions:

```bash
python scripts/resize_images.py --resolutions 448 1280
```

## Results

```text
results/images/<Task>/
├── Reference_dataset/
├── Test_dataset/
└── Train_dataset/
```

The output name includes the selected resolution, for example:

```text
test_Else_944_p1280.jpg
```
