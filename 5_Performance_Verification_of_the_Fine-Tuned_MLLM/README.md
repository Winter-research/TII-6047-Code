# Performance Verification of the Fine-Tuned MLLM

This module evaluates the fine-tuned MLLM on Task1--Task3 through the native Ollama multimodal API. The outputs are divided into model responses, grading performance, and CoT reliability.

## Structure

```text
5_Performance_Verification_of_the_Fine-Tuned_MLLM/
├── configs/
│   ├── commercial_judge.yaml
│   ├── ollama_model.yaml
│   └── tasks.yaml
├── scripts/
│   ├── dg_prompt.py
│   ├── performance_test.py
│   ├── calculate_metrics.py
│   └── common.py
├── results/
│   ├── performance_testing/
│   │   ├── Task1/
│   │   ├── Task2/
│   │   └── Task3/
│   ├── grading_performance/
│   │   ├── Task1/
│   │   ├── Task2/
│   │   └── Task3/
│   └── cot_reliability/
│       ├── Task1/
│       ├── Task2/
│       └── Task3/
├── .env.example
└── README.md
```

## Setup

```bash
python -m pip install requests PyYAML openai
ollama serve
```

The Ollama endpoint, runtime model, and generation parameters are set in `configs/ollama_model.yaml`. The commercial CoT judge is set in `configs/commercial_judge.yaml`; its API credentials are read from `.env`.

## Performance Testing

Run all tasks:

```bash
python scripts/performance_test.py
```

Run one task:

```bash
python scripts/performance_test.py --tasks Task1
```

Outputs are saved to:

```text
results/performance_testing/<Task>/Prompt4/<Model>/
```

## Evaluation

```bash
python scripts/calculate_metrics.py
```

Run one task:

```bash
python scripts/calculate_metrics.py --task Task1
```

Grading performance includes ACC, macro precision, macro recall, MF1, NMAE, R_K, and over-/under-grading rates:

```text
results/grading_performance/<Task>/
```

CoT reliability includes complete-correctness accuracy and visual/logical hallucination rates. Completed judge responses are cached for resumable evaluation:

```text
results/cot_reliability/<Task>/
```

Use `--skip-cot-api` to calculate grading performance only. This mode does not call the commercial judge or create CoT result files.
