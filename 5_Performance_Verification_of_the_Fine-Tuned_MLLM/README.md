# Performance Verification of the Fine-Tuned MLLM

This module tests the fine-tuned MLLM through Ollama and calculates grading and CoT reliability metrics for Task1--Task3.

## Structure

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
│   ├── performance_testing/
│   ├── grading_performance/
│   └── cot_reliability/
├── .env.example
└── README.md
```

## Files

| File | Function |
|---|---|
| `configs/ollama_model.yaml` | Ollama endpoint, model name, image resolution, generation parameters, and retry settings. |
| `configs/commercial_judge.yaml` | Model and request parameters for CoT evaluation. |
| `configs/tasks.yaml` | Data directories and grade labels for Task1--Task3. |
| `scripts/common.py` | Configuration loading, path handling, prompt-component loading, and API client setup. |
| `scripts/dg_prompt.py` | Constructs the Prompt 4 multimodal messages for the three tasks. |
| `scripts/performance_test.py` | Sends test samples to Ollama and saves one response JSON per image. |
| `scripts/calculate_metrics.py` | Calculates grading metrics and generates the CoT evaluation records. |
| `Metrics/` | Project-level implementations of the grading and CoT metrics. |

## Configuration

The Ollama model is set in `configs/ollama_model.yaml`:

```yaml
model: Multi-Task_Fine-tuned_MLLM:latest
```

The CoT judge reads its model settings from `configs/commercial_judge.yaml` and its connection information from `.env`:

```text
COMMERCIAL_MLLM_API_KEY=
COMMERCIAL_MLLM_BASE_URL=
```

Task paths and grade labels are set in `configs/tasks.yaml`.

## Data

```text
Data/Sample_Dataset/<Task>/
├── Reference_dataset/*.json
└── Test_dataset/*.json

1_Data_Processing/results/images/<Task>/
├── Reference_dataset/*_p1280.jpg
└── Test_dataset/*_p1280.jpg

Prompt_Components/<Task>.py
```

## Run

Install the dependencies and start Ollama:

```bash
python -m pip install requests PyYAML openai
ollama serve
```

Run all tasks or one selected task:

```bash
python scripts/performance_test.py
python scripts/performance_test.py --tasks Task1
```

Calculate all metrics, one task, or grading metrics only:

```bash
python scripts/calculate_metrics.py
python scripts/calculate_metrics.py --task Task1
python scripts/calculate_metrics.py --task Task1 --skip-cot-api
```

## Results

```text
results/
├── performance_testing/<Task>/Prompt4/
│   ├── prompt.txt
│   └── Multi-Task_Fine-tuned_MLLM/<test_image>.json
├── grading_performance/<Task>/
│   ├── Grading_Metrics.csv
│   └── Grading_Metrics_Details.json
└── cot_reliability/<Task>/
    ├── <test_image>.json
    └── CoT_Evaluation_Records.csv
```

| Output | Content |
|---|---|
| `prompt.txt` | Prompt 4 rendered as readable text. |
| `performance_testing/.../<test_image>.json` | Model response, extracted grade, ground-truth grade, and correctness. |
| `Grading_Metrics.csv` | ACC, macro precision, macro recall, MF1, NMAE, highest-severity recall, and over-/under-grading rates. |
| `Grading_Metrics_Details.json` | Confusion matrix, per-class values, missing results, and unparsed responses. |
| `cot_reliability/.../<test_image>.json` | Per-image visual and logical CoT evaluation. |
| `CoT_Evaluation_Records.csv` | One CoT evaluation record per image. |
