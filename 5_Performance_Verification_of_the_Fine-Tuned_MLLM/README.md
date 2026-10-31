# Performance Verification of the Fine-Tuned MLLM

[中文说明](README_zh.md)

This module evaluates the fine-tuned MLLM on Task1, Task2, and Task3 through the native Ollama multimodal API. It calculates grading-performance metrics and commercial-MLLM-assisted CoT reliability metrics.

## Structure

```text
5_Performance_Verification_of_the_Fine-Tuned_MLLM/
├── configs/
│   ├── ollama_model.yaml
│   └── tasks.yaml
├── scripts/
│   ├── dg_prompt.py
│   ├── performance_test.py
│   ├── calculate_metrics.py
│   └── common.py
├── results/
│   ├── Task1/
│   │   ├── performance_testing/
│   │   └── metrics/
│   ├── Task2/
│   ├── Task3/
│   └── Multi-Task/
├── .env.example
├── README.md
└── README_zh.md
```

Each task stores its model responses, metric outputs, CoT evaluation details, and resumable CoT cache under one task directory. `Multi-Task` contains only the cross-task metric summary.

## Setup

```bash
python -m pip install requests PyYAML openai
ollama serve
```

Create the commercial judge configuration used by the CoT evaluator:

```powershell
Copy-Item .env.example .env
```

```text
COMMERCIAL_MLLM_API_KEY=your-api-key
COMMERCIAL_MLLM_BASE_URL=https://your-api-endpoint/v1
```

The Ollama URL, runtime model, resolution, and generation parameters are defined in `configs/ollama_model.yaml`.

## Performance Testing

Run all tasks:

```bash
python scripts/performance_test.py
```

Run selected tasks:

```bash
python scripts/performance_test.py --tasks Task1
```

## Metrics

Run all tasks:

```bash
python scripts/calculate_metrics.py
```

Run one task independently:

```bash
python scripts/calculate_metrics.py --task Task1
```

Each completed CoT evaluation is saved immediately. Re-running the same command skips cached samples and resumes from the first unfinished sample. If the commercial judge is temporarily unavailable, conventional grading metrics and the current CoT progress are still saved.

Task outputs:

```text
results/<Task>/metrics/Metrics.csv
results/<Task>/metrics/Metrics_Details.json
results/<Task>/metrics/CoT_Evaluation_Cache.json
```

Cross-task outputs:

```text
results/Multi-Task/metrics/Metrics.csv
results/Multi-Task/metrics/Metrics_Details.json
```
