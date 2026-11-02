import argparse
import csv
import json

from common import RESULTS_DIR


def result_rows(task_name, prompt_number=None):
    task_dir = RESULTS_DIR / "performance_testing" / task_name
    prompt_dirs = (
        [task_dir / f"Prompt{prompt_number}"]
        if prompt_number is not None
        else sorted(task_dir.glob("Prompt*"), key=lambda path: path.name)
    )

    rows = []
    for prompt_dir in prompt_dirs:
        if not prompt_dir.is_dir():
            continue
        for model_dir in sorted(
            (path for path in prompt_dir.iterdir() if path.is_dir()),
            key=lambda path: path.name,
        ):
            records = []
            for path in sorted(model_dir.glob("test_*.json"), key=lambda item: item.name):
                if path.stem.endswith("_zh"):
                    continue
                records.append(json.loads(path.read_text(encoding="utf-8")))
            if not records:
                continue

            correct = sum(
                int(record.get("correct", record.get("answer") == record.get("true_grade")))
                for record in records
            )
            total = len(records)
            rows.append(
                {
                    "task": task_name,
                    "prompt": prompt_dir.name,
                    "model": records[0].get("model", model_dir.name),
                    "sample_count": total,
                    "correct": correct,
                    "ACC (%)": round(correct / total * 100, 4),
                }
            )
    if not rows:
        raise FileNotFoundError(f"No performance-test results found for {task_name}")
    return rows


def write_accuracy(task_name, rows):
    output_dir = RESULTS_DIR / "accuracy" / task_name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "Accuracy.csv"
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(description="Calculate grading accuracy (ACC).")
    parser.add_argument("--task", required=True, choices=["Task1", "Task2", "Task3"])
    parser.add_argument("--prompt", type=int, choices=[1, 2, 3, 4])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    output = write_accuracy(args.task, result_rows(args.task, args.prompt))
    print(f"Accuracy saved: {output}")
