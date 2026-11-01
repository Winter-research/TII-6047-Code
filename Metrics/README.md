# Metrics

```text
Metrics/
├── __init__.py
├── grading_performance_metrics.py
├── cot_reliability_metrics.py
└── README.md
```

## Grading Metrics

`grading_performance_metrics.py` calculates:

| Metric | Meaning |
|---|---|
| `ACC` | Grading accuracy |
| `MP` | Macro precision |
| `MR` | Macro recall |
| `MF1` | Macro F1 score |
| `NMAE` | Normalized grade-distance error |
| `R_K` | Recall of the highest-severity grade |
| `over_grading_rate` | Proportion of predictions above the ground-truth grade |
| `under_grading_rate` | Proportion of predictions below the ground-truth grade |

List `labels` from the lowest to the highest severity because `NMAE`, `R_K`, and the two grading-error rates use this order.

```python
from Metrics import grading_metrics

values = grading_metrics(
    y_true=["Else", "Kind", "Major"],
    y_pred=["Else", "Major", "Kind"],
    labels=["Else", "Kind", "Major"],
)
```

## CoT Metrics

`cot_reliability_metrics.py` checks JSON validity (`J`), decision branches (`B`), final grade (`F`), visual description (`V`), and logical reasoning (`L`). It reports:

| Metric | Meaning |
|---|---|
| `ACC_FC_MCoT` | Proportion of samples for which J, B, F, V, and L are all correct |
| `VHR_CoT` | Visual hallucination rate |
| `LHR_CoT` | Logical hallucination rate |

The V and L checks use the commercial MLLM configured in Module 5.

## Run

```bash
python 5_Performance_Verification_of_the_Fine-Tuned_MLLM/scripts/calculate_metrics.py --task Task1
```

Results are saved to `5_Performance_Verification_of_the_Fine-Tuned_MLLM/results/Task1/metrics/`.
