# Performance Verification of the Fine-Tuned MLLM

This module runs the fine-tuned multimodal model through Ollama and evaluates its grading results and chain-of-thought (CoT) reliability for Task1--Task3.

## Directory Structure

```text
5_Performance_Verification_of_the_Fine-Tuned_MLLM/
├── configs/
│   ├── ollama_model.yaml
│   ├── commercial_judge.yaml
│   └── tasks.yaml
├── scripts/
│   ├── common.py
│   ├── dg_prompt.py
│   ├── performance_test.py
│   └── calculate_metrics.py
├── results/
│   ├── performance_testing/<Task>/Prompt4/
│   ├── grading_performance/<Task>/
│   └── cot_reliability/<Task>/
├── .env.example
└── README.md
```

## Files

| File | Purpose |
|---|---|
| `configs/ollama_model.yaml` | Defines the Ollama API URL, runtime model, output model name, image resolution, generation parameters, timeout, and retry settings. |
| `configs/commercial_judge.yaml` | Defines the commercial model and request parameters used to assess visual and logical errors in the generated CoT. |
| `configs/tasks.yaml` | Maps Task1--Task3 to their sample-data and resized-image directories and defines the available grading labels. |
| `scripts/common.py` | Loads YAML and environment settings, locates project directories, loads prompt components, creates the commercial-model client, and provides common JSON/path utilities. |
| `scripts/dg_prompt.py` | Builds the Task1, Task2, and Task3 multimodal message sequences. It inserts the system prompt, reference images and answers, objective image, and grading question in their required order. |
| `scripts/performance_test.py` | Loads the reference and test data, calls the fine-tuned model through Ollama, extracts the predicted grade, and saves one result JSON for each test image. |
| `scripts/calculate_metrics.py` | Reads the saved performance-test JSON files, calculates grading metrics, calls the commercial CoT judge when enabled, and writes task-specific evaluation files. |
| `.env.example` | Lists the environment variables required by the commercial CoT judge. Copy it to `.env` and provide the API key and base URL before running CoT evaluation. |
| `README.md` | Describes the module structure, configuration, commands, and output files. |

The reusable metric functions imported by `calculate_metrics.py` are stored in the project-level `Metrics/` package.

## Input Data

The paths are read from `configs/tasks.yaml`.

```text
Data/Sample_Dataset/<Task>/
├── Reference_dataset/reference_*.json
└── Test_dataset/test_*.json

1_Data_Processing/results/images/<Task>/
├── Reference_dataset/reference_*_p1280.jpg
└── Test_dataset/test_*_p1280.jpg
```

The reference JSON and image stems must match. The same rule applies to each test JSON and test image.

## Setup

Run the following commands from this module directory:

```bash
python -m pip install requests PyYAML openai
ollama serve
```

The default runtime model is configured in `configs/ollama_model.yaml`:

```yaml
model: paper_gllm_joint_language_p1280_e300:latest
```

For CoT evaluation, copy `.env.example` to `.env` and fill in:

```text
COMMERCIAL_MLLM_API_KEY=
COMMERCIAL_MLLM_BASE_URL=
```

## Performance Testing

Check the prompt and data paths without calling Ollama:

```bash
python scripts/performance_test.py --limit 1 --dry-run
```

Run all three tasks:

```bash
python scripts/performance_test.py
```

Run one task:

```bash
python scripts/performance_test.py --tasks Task1
```

Use `--overwrite` to regenerate existing image results. The `--model`, `--ollama-url`, and `--result-model-name` options temporarily override the corresponding YAML settings.

Performance-test outputs are stored as follows:

```text
results/performance_testing/<Task>/Prompt4/
├── prompt.txt
└── <Model>/<test_image_stem>.json
```

- `prompt.txt` is the readable prompt preview generated from the current prompt components.
- Each test-image JSON records the image path, true grade, raw model response, extracted answer, correctness, model name, and prompt setting.

## Metric Calculation

Calculate grading and CoT metrics for all tasks:

```bash
python scripts/calculate_metrics.py
```

Calculate one task:

```bash
python scripts/calculate_metrics.py --task Task1
```

Calculate grading metrics without calling the commercial CoT judge:

```bash
python scripts/calculate_metrics.py --task Task1 --skip-cot-api
```

Evaluate a limited number of new CoT samples:

```bash
python scripts/calculate_metrics.py --task Task1 --cot-limit 1
```

Use `--cot-json-only` when only the per-image CoT JSON files are needed. In this mode, the task-level CoT CSV is not retained.

## Outputs

### Grading performance

```text
results/grading_performance/<Task>/
├── Grading_Metrics.csv
└── Grading_Metrics_Details.json
```

- `Grading_Metrics.csv` contains the task-level ACC, macro precision, macro recall, MF1, NMAE, highest-severity recall, and over-/under-grading rates.
- `Grading_Metrics_Details.json` contains the confusion matrix, per-class results, missing result files, and responses whose grades could not be parsed.

### CoT reliability

```text
results/cot_reliability/<Task>/
├── <test_image_stem>.json
└── CoT_Evaluation_Records.csv
```

- Each image JSON stores the first visual or logical error identified by the judge and the corresponding CoT indicators.
- `CoT_Evaluation_Records.csv` records one evaluated image per row. It is written after all CoT samples for the selected task have been evaluated.

All stored repository paths use `/` and are relative to the relevant module or project root.
