import argparse
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SECTION_DIR = SCRIPT_DIR.parent
TASK_NAMES = ("Task1", "Task2", "Task3")
GRADE_ORDERS = {
    "Task1": ["一般", "重大"],
    "Task2": ["其他", "一般", "重大"],
    "Task3": ["其他", "一般", "重大", "紧急"],
}
ENGLISH_GRADE_MAP = {
    "else": "其他",
    "kind": "一般",
    "major": "重大",
    "urgent": "紧急",
}


def find_project_root():
    for parent in Path(__file__).resolve().parents:
        if (parent / "Data" / "Sample_Dataset").is_dir() and (parent / "Metrics").is_dir():
            return parent
    raise FileNotFoundError("Cannot locate the TII-6047-Code project root")


PROJECT_ROOT = find_project_root()
sys.path.insert(0, str(PROJECT_ROOT))

from common import RESULTS_DIR, runtime_settings  # noqa: E402

from Metrics import (  # noqa: E402
    JUDGE_MODEL,
    confusion_matrix,
    cot_reliability_metrics,
    evaluate_cot_sample,
    grading_metrics,
    per_class_precision_recall_f1,
)


SETTINGS = runtime_settings()
DEFAULT_RESULT_MODEL_NAME = SETTINGS["result_model_name"]
RESOLUTION = SETTINGS["resolution"]
def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate all grading and CoT metrics for the fine-tuned MLLM."
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--task",
        choices=TASK_NAMES,
        help="Calculate one task and save task-specific metric files.",
    )
    selection.add_argument(
        "--tasks",
        nargs="+",
        choices=TASK_NAMES,
        help="Calculate selected tasks. The default is all three tasks.",
    )
    parser.add_argument(
        "--result-model-name",
        default=DEFAULT_RESULT_MODEL_NAME,
        help="Result subdirectory name under Result_Task1, Result_Task2, and Result_Task3.",
    )
    parser.add_argument(
        "--skip-cot-api",
        action="store_true",
        help="Calculate grading metrics only and skip API-based CoT evaluation.",
    )
    args = parser.parse_args()
    if args.task:
        args.tasks = [args.task]
    elif not args.tasks:
        args.tasks = list(TASK_NAMES)
    return args


def percentage(value):
    return round(value * 100, 4)


def extract_grade(response_text, allowed_grades):
    text = str(response_text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)

    try:
        start = cleaned.index("{")
        end = cleaned.rindex("}") + 1
        data = json.loads(cleaned[start:end])
        if isinstance(data, dict):
            for key in ("grade_result", "grade", "result", "label", "answer", "定级结果", "缺陷等级"):
                if key not in data:
                    continue
                value = str(data[key]).split("|", 1)[0].strip()
                if value in allowed_grades:
                    return value
                mapped = ENGLISH_GRADE_MAP.get(value.lower())
                if mapped in allowed_grades:
                    return mapped
    except (ValueError, json.JSONDecodeError):
        pass

    chinese_matches = re.findall(r"紧急|重大|一般|其他", cleaned)
    for value in reversed(chinese_matches):
        if value in allowed_grades:
            return value

    english_matches = re.findall(r"\b(?:Else|Kind|Major|Urgent)\b", cleaned, re.IGNORECASE)
    for value in reversed(english_matches):
        mapped = ENGLISH_GRADE_MAP[value.lower()]
        if mapped in allowed_grades:
            return mapped
    return ""


def expected_test_images(task):
    test_dir = PROJECT_ROOT / "Data" / "Sample_Dataset" / task / "Test_dataset"
    return sorted(test_dir.glob(f"test_*_p{RESOLUTION}.jpg"))


def result_root(task):
    return RESULTS_DIR / task / "performance_testing" / "Prompt4"


def task_metrics_dir(task):
    return RESULTS_DIR / task / "metrics"


def multi_task_metrics_dir():
    return RESULTS_DIR / "Multi-Task" / "metrics"


def find_model_result_dir(task, result_model_name):
    candidate = result_root(task) / result_model_name
    return candidate if candidate.is_dir() else None


def load_task_records(task, result_model_name):
    model_dir = find_model_result_dir(task, result_model_name)
    if model_dir is None:
        return [], None

    records = []
    required = {"picture", "true_grade", "response", "model", "prompt_setting"}
    for path in sorted(model_dir.glob("test_*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        missing = required - set(record)
        if missing:
            raise ValueError(f"Missing fields in {path}: {sorted(missing)}")
        record["result_path"] = str(path.relative_to(SECTION_DIR))
        record["source_path"] = str(path)
        records.append(record)
    return records, model_dir


def expert_paths(task, record):
    stem = Path(record["picture"]).stem
    stem = re.sub(r"_p\d+$", "", stem)
    test_dir = PROJECT_ROOT / "Data" / "Sample_Dataset" / task / "Test_dataset"
    json_path = test_dir / f"{stem}.json"
    image_path = test_dir / record["picture"]
    if not json_path.is_file():
        raise FileNotFoundError(f"Missing expert annotation: {json_path}")
    if not image_path.is_file():
        raise FileNotFoundError(f"Missing test image: {image_path}")
    return json_path, image_path


def load_cache(path):
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_cache(path, cache):
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cot_cache_key(task, record, expert_cot):
    payload = json.dumps(
        {
            "task": task,
            "judge_model": JUDGE_MODEL,
            "result_path": record["result_path"],
            "response": record["response"],
            "expert_cot": expert_cot,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def find_legacy_cache_entry(cache, task, record):
    result_name = Path(record["result_path"]).name
    for item in cache.values():
        if item.get("task") != task or item.get("judge_model") != JUDGE_MODEL:
            continue
        if Path(str(item.get("result_path", ""))).name == result_name:
            return item.get("evaluation")
    return None


def normalize_task_cache(task, records, cache, cache_path):
    normalized = {}
    for record in records:
        expert_path, _ = expert_paths(task, record)
        expert_cot = json.loads(expert_path.read_text(encoding="utf-8"))
        key = cot_cache_key(task, record, expert_cot)
        if key in cache:
            normalized[key] = cache[key]
            continue
        legacy_evaluation = find_legacy_cache_entry(cache, task, record)
        if legacy_evaluation is not None:
            normalized[key] = {
                "task": task,
                "result_path": record["result_path"],
                "judge_model": JUDGE_MODEL,
                "evaluation": legacy_evaluation,
            }
    if normalized != cache:
        save_cache(cache_path, normalized)
    return normalized


def evaluate_cot_records(task, records, cache, cache_path):
    evaluations = []
    failed_record = None
    error_message = None
    for index, record in enumerate(records, start=1):
        expert_path, image_path = expert_paths(task, record)
        expert_cot = json.loads(expert_path.read_text(encoding="utf-8"))
        key = cot_cache_key(task, record, expert_cot)
        if key not in cache:
            legacy_evaluation = find_legacy_cache_entry(cache, task, record)
            if legacy_evaluation is not None:
                cache[key] = {
                    "task": task,
                    "result_path": record["result_path"],
                    "judge_model": JUDGE_MODEL,
                    "evaluation": legacy_evaluation,
                }
                save_cache(cache_path, cache)
                evaluations.append(legacy_evaluation)
                continue

            print(f"CoT evaluation {task} [{index}/{len(records)}]: {record['picture']}")
            try:
                evaluation = evaluate_cot_sample(
                    record["response"],
                    expert_cot,
                    image_path,
                )
            except Exception as error:
                failed_record = record["picture"]
                error_message = str(error)
                print(
                    f"CoT evaluation paused at {task} [{index}/{len(records)}] "
                    f"{failed_record}: {error}"
                )
                break
            cache[key] = {
                "task": task,
                "result_path": record["result_path"],
                "judge_model": JUDGE_MODEL,
                "evaluation": evaluation,
            }
            save_cache(cache_path, cache)
        evaluations.append(cache[key]["evaluation"])
    return {
        "evaluations": evaluations,
        "completed": len(evaluations),
        "total": len(records),
        "complete": len(evaluations) == len(records),
        "failed_record": failed_record,
        "error": error_message,
    }


def grading_details(y_true, y_pred, labels):
    return {
        "labels": labels,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels),
        "per_class": per_class_precision_recall_f1(y_true, y_pred, labels),
    }


def calculate_task(task, result_model_name, skip_cot_api, cache, cache_path):
    expected = expected_test_images(task)
    records, model_dir = load_task_records(task, result_model_name)
    cache = normalize_task_cache(task, records, cache, cache_path)
    expected_names = {path.name for path in expected}
    result_names = {record["picture"] for record in records}
    missing_names = sorted(expected_names - result_names)
    labels = GRADE_ORDERS[task]

    for record in records:
        answer = str(record.get("answer", "")).strip()
        if answer not in labels:
            answer = extract_grade(record["response"], labels)
        record["parsed_answer"] = answer

    unparsed = [record["picture"] for record in records if record["parsed_answer"] not in labels]
    complete = not missing_names and not unparsed and len(records) == len(expected)
    row = {
        "task": task,
        "model": result_model_name,
        "prompt_setting": records[0]["prompt_setting"] if records else "Prompt 4",
        "expected_count": len(expected),
        "result_count": len(records),
        "parsed_count": len(records) - len(unparsed),
        "missing_count": len(missing_names),
        "unparsed_count": len(unparsed),
        "ACC (%)": "N/A",
        "MP (%)": "N/A",
        "MR (%)": "N/A",
        "MF1 (%)": "N/A",
        "NMAE (%)": "N/A",
        "R_K (%)": "N/A",
        "over_grading_rate (%)": "N/A",
        "under_grading_rate (%)": "N/A",
        "ACC_FC_MCoT (%)": "N/A",
        "VHR_CoT (%)": "N/A",
        "LHR_CoT (%)": "N/A",
        "status": "complete" if complete else "incomplete_or_unparsed",
    }
    details = {
        "task": task,
        "model": result_model_name,
        "recorded_models": sorted({str(record.get("model", "")) for record in records}),
        "result_directory": str(model_dir) if model_dir else None,
        "missing_results": missing_names,
        "unparsed_results": unparsed,
    }

    if complete:
        y_true = [record["true_grade"] for record in records]
        y_pred = [record["parsed_answer"] for record in records]
        metrics = grading_metrics(y_true, y_pred, labels)
        for key in ("ACC", "MP", "MR", "MF1", "NMAE", "R_K"):
            row[f"{key} (%)"] = percentage(metrics[key])
        row["over_grading_rate (%)"] = percentage(metrics["over_grading_rate"])
        row["under_grading_rate (%)"] = percentage(metrics["under_grading_rate"])
        details["grading"] = grading_details(y_true, y_pred, labels)

    if records and not skip_cot_api:
        cot_progress = evaluate_cot_records(task, records, cache, cache_path)
        details["cot_progress"] = {
            key: value
            for key, value in cot_progress.items()
            if key != "evaluations"
        }
        details["cot_evaluations"] = cot_progress["evaluations"]
        if cot_progress["complete"]:
            cot_metrics = cot_reliability_metrics(cot_progress["evaluations"])
            row["ACC_FC_MCoT (%)"] = percentage(cot_metrics["ACC_FC_MCoT"])
            row["VHR_CoT (%)"] = percentage(cot_metrics["VHR_CoT"])
            row["LHR_CoT (%)"] = percentage(cot_metrics["LHR_CoT"])
        else:
            row["status"] = "cot_incomplete"

    return row, details


def average_row(rows):
    metric_columns = [
        "ACC (%)",
        "MP (%)",
        "MR (%)",
        "MF1 (%)",
        "NMAE (%)",
        "R_K (%)",
        "over_grading_rate (%)",
        "under_grading_rate (%)",
        "ACC_FC_MCoT (%)",
        "VHR_CoT (%)",
        "LHR_CoT (%)",
    ]
    row = {
        "task": "Task_Average",
        "model": rows[0]["model"],
        "prompt_setting": rows[0]["prompt_setting"],
        "expected_count": sum(item["expected_count"] for item in rows),
        "result_count": sum(item["result_count"] for item in rows),
        "parsed_count": sum(item["parsed_count"] for item in rows),
        "missing_count": sum(item["missing_count"] for item in rows),
        "unparsed_count": sum(item["unparsed_count"] for item in rows),
        "status": "complete" if all(item["status"] == "complete" for item in rows) else "incomplete_or_unparsed",
    }
    for column in metric_columns:
        values = [item[column] for item in rows if isinstance(item[column], (int, float))]
        row[column] = round(sum(values) / len(values), 4) if values else "N/A"
    return row


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    rows = []
    details = {}

    for task in args.tasks:
        metrics_dir = task_metrics_dir(task)
        metrics_dir.mkdir(parents=True, exist_ok=True)
        cache_path = metrics_dir / "CoT_Evaluation_Cache.json"
        cache = load_cache(cache_path)
        row, task_details = calculate_task(
            task,
            args.result_model_name,
            args.skip_cot_api,
            cache,
            cache_path,
        )
        rows.append(row)
        details[task] = task_details
        task_csv_path = metrics_dir / "Metrics.csv"
        task_details_path = metrics_dir / "Metrics_Details.json"
        write_csv(task_csv_path, [row])
        task_details_path.write_text(
            json.dumps({task: task_details}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            f"{task}: results={row['result_count']}/{row['expected_count']}, "
            f"parsed={row['parsed_count']}, status={row['status']}"
        )
        print(f"Task metrics: {task_csv_path}")
        print(f"Task details: {task_details_path}")

    if len(rows) > 1:
        summary_rows = rows + [average_row(rows)]
        metrics_dir = multi_task_metrics_dir()
        metrics_dir.mkdir(parents=True, exist_ok=True)
        csv_path = metrics_dir / "Metrics.csv"
        details_path = metrics_dir / "Metrics_Details.json"
        write_csv(csv_path, summary_rows)
        details_path.write_text(
            json.dumps(details, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Multi-task metrics: {csv_path}")
        print(f"Multi-task details: {details_path}")


if __name__ == "__main__":
    main()

