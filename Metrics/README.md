# Metrics

This package provides the grading-performance and CoT-reliability metrics.

## Structure

```text
Metrics/
├── __init__.py
├── grading_performance_metrics.py
├── cot_reliability_metrics.py
└── README.md
```

## Files

| File | Function |
|---|---|
| `__init__.py` | Exports the public metric functions. |
| `grading_performance_metrics.py` | Classification, grade-distance, and over-/under-grading metrics. |
| `cot_reliability_metrics.py` | JSON, decision-branch, final-grade, visual, and logical CoT evaluation. |

## Inputs

Grading metrics receive the true labels, predicted labels, and ordered grade list. CoT evaluation receives the model response, expert-reviewed JSON, and objective image.

| Metric | Meaning |
|---|---|
| `ACC` | Grading accuracy. |
| `MP` | Macro precision. |
| `MR` | Macro recall. |
| `MF1` | Macro F1. |
| `NMAE` | Normalized grade-distance error. |
| `R_K` | Highest-severity recall. |
| `over_grading_rate` | Rate of predictions above the true grade. |
| `under_grading_rate` | Rate of predictions below the true grade. |
| `ACC_FC_MCoT` | Rate of fully correct CoT responses. |
| `VHR_CoT` | Visual hallucination rate. |
| `LHR_CoT` | Logical hallucination rate. |

## Public Functions

| Function | Return value |
|---|---|
| `grading_metrics()` | Complete grading metric dictionary. |
| `confusion_matrix()` | Grade confusion matrix. |
| `per_class_precision_recall_f1()` | Precision, recall, and F1 for each grade. |
| `evaluate_cot_sample()` | J, B, F, V, L, hallucination indicators, and first-error information for one sample. |
| `cot_reliability_metrics()` | Aggregate CoT reliability metrics. |
