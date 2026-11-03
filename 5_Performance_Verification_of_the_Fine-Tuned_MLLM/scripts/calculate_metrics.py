import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SECTION_DIR = SCRIPT_DIR.parent
TASK_NAMES = ("Task1", "Task2", "Task3")
GRADE_ORDERS = {
    "Task1": ["Else", "Kind"],
    "Task2": ["Else", "Kind", "Major"],
    "Task3": ["Else", "Kind", "Major", "Urgent"],
}


def find_project_root():
    for parent in Path(__file__).resolve().parents:
        if (parent / "Data" / "Sample_Dataset").is_dir() and (parent / "Metrics").is_dir():
            return parent
    raise FileNotFoundError("Cannot locate the TII-6047-Code project root")


PROJECT_ROOT = find_project_root()
sys.path.insert(0, str(PROJECT_ROOT))

from common import (  # noqa: E402
    RESULTS_DIR,
    commercial_mllm_client,
    cot_judge_settings,
    runtime_settings,
)

from Metrics import (  # noqa: E402
    confusion_matrix,
    cot_reliability_metrics,
    evaluate_cot_sample,
    grading_metrics,
    per_class_precision_recall_f1,
)


SETTINGS = runtime_settings()
JUDGE_SETTINGS = cot_judge_settings()
JUDGE_MODEL = JUDGE_SETTINGS["model"]
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
        help="Model result directory under results/performance_testing/<Task>/Prompt4.",
    )
    parser.add_argument(
        "--skip-cot-api",
        action="store_true",
        help="Calculate grading metrics only and skip API-based CoT evaluation.",
    )
    parser.add_argument(
        "--cot-limit",
        type=int,
        default=0,
        help="Maximum number of new CoT samples to evaluate in this run; 0 means no limit.",
    )
    parser.add_argument(
        "--cot-json-only",
        action="store_true",
        help="Generate per-image CoT evaluation JSON files without summary CSV files.",
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
            for key in ("grade_result", "grade", "result", "label", "answer"):
                if key not in data:
                    continue
                value = str(data[key]).split("|", 1)[0].strip()
                if value in allowed_grades:
                    return value
    except (ValueError, json.JSONDecodeError):
        pass

    english_matches = re.findall(r"\b(?:Else|Kind|Major|Urgent)\b", cleaned, re.IGNORECASE)
    for value in reversed(english_matches):
        normalized = value.title()
        if normalized in allowed_grades:
            return normalized
    return ""


def expected_test_images(task):
    test_dir = (
        PROJECT_ROOT
        / "1_Data_Processing"
        / "results"
        / "images"
        / task
        / "Test_dataset"
    )
    return sorted(test_dir.glob(f"test_*_p{RESOLUTION}.jpg"))


def result_root(task):
    return RESULTS_DIR / "performance_testing" / task / "Prompt4"


def grading_metrics_dir(task):
    return RESULTS_DIR / "grading_performance" / task


def cot_metrics_dir(task):
    return RESULTS_DIR / "cot_reliability" / task


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
        if path.stem.endswith("_zh"):
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        missing = required - set(record)
        if missing:
            raise ValueError(f"Missing fields in {path}: {sorted(missing)}")
        record["result_path"] = path.relative_to(SECTION_DIR).as_posix()
        record["source_path"] = str(path)
        records.append(record)
    return records, model_dir


def expert_paths(task, record):
    stem = Path(record["picture"]).stem
    stem = re.sub(r"_p\d+$", "", stem)
    test_dir = PROJECT_ROOT / "Data" / "Sample_Dataset" / task / "Test_dataset"
    image_dir = (
        PROJECT_ROOT
        / "1_Data_Processing"
        / "results"
        / "images"
        / task
        / "Test_dataset"
    )
    json_path = test_dir / f"{stem}.json"
    image_path = image_dir / record["picture"]
    if not json_path.is_file():
        raise FileNotFoundError(f"Missing expert annotation: {json_path}")
    if not image_path.is_file():
        raise FileNotFoundError(f"Missing test image: {image_path}")
    return json_path, image_path


def cot_evaluation_path(task, record):
    image_stem = Path(record["picture"]).stem
    return cot_metrics_dir(task) / f"{image_stem}.json"


def load_cot_evaluation(path, record):
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("judge_model") != JUDGE_MODEL:
        return None
    if data.get("objective_image") != record["picture"]:
        return None
    if data.get("result_path") != record["result_path"]:
        return None
    return data.get("evaluation")


def save_cot_evaluation(path, task, record, evaluation):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "task": task,
        "objective_image": record["picture"],
        "result_path": record["result_path"],
        "judge_model": JUDGE_MODEL,
        "evaluation": evaluation,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def evaluate_cot_records(
    task,
    records,
    judge_client,
    judge_settings,
    cot_limit,
):
    evaluations = []
    failed_record = None
    error_message = None
    new_evaluations = 0
    for index, record in enumerate(records, start=1):
        expert_path, image_path = expert_paths(task, record)
        expert_cot = json.loads(expert_path.read_text(encoding="utf-8"))
        evaluation_path = cot_evaluation_path(task, record)
        evaluation = load_cot_evaluation(
            evaluation_path,
            record,
        )
        if evaluation is None:
            if cot_limit > 0 and new_evaluations >= cot_limit:
                break
            print(f"CoT evaluation {task} [{index}/{len(records)}]: {record['picture']}")
            try:
                evaluation = evaluate_cot_sample(
                    record["response"],
                    expert_cot,
                    image_path,
                    judge_client,
                    judge_settings,
                )
            except Exception as error:
                failed_record = record["picture"]
                error_message = str(error)
                print(
                    f"CoT evaluation paused at {task} [{index}/{len(records)}] "
                    f"{failed_record}: {error}"
                )
                break
            save_cot_evaluation(
                evaluation_path,
                task,
                record,
                evaluation,
            )
            new_evaluations += 1
        evaluations.append(evaluation)
    return {
        "evaluations": evaluations,
        "completed": len(evaluations),
        "total": len(records),
        "complete": len(evaluations) == len(records),
        "failed_record": failed_record,
        "error": error_message,
    }


def cached_cot_records(task, records):
    evaluations = []
    for record in records:
        evaluation = load_cot_evaluation(
            cot_evaluation_path(task, record),
            record,
        )
        if evaluation is None:
            break
        evaluations.append(evaluation)
    return {
        "evaluations": evaluations,
        "completed": len(evaluations),
        "total": len(records),
        "complete": len(evaluations) == len(records),
        "failed_record": None,
        "error": None,
    }


def grading_details(y_true, y_pred, labels):
    return {
        "labels": labels,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels),
        "per_class": per_class_precision_recall_f1(y_true, y_pred, labels),
    }


def calculate_task(
    task,
    result_model_name,
    skip_cot_api,
    judge_client,
    judge_settings,
    cot_limit,
):
    expected = expected_test_images(task)
    records, model_dir = load_task_records(task, result_model_name)
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
        "cot_evaluated_count": 0,
        "cot_pending_count": len(records),
        "grading_status": "complete" if complete else "incomplete_or_unparsed",
        "cot_status": "skipped" if skip_cot_api else "pending",
    }
    details = {
        "task": task,
        "model": result_model_name,
        "recorded_models": sorted({str(record.get("model", "")) for record in records}),
        "result_directory": (
            model_dir.relative_to(SECTION_DIR).as_posix() if model_dir else None
        ),
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

    if records:
        if skip_cot_api:
            cot_progress = cached_cot_records(task, records)
        else:
            cot_progress = evaluate_cot_records(
                task,
                records,
                judge_client,
                judge_settings,
                cot_limit,
            )
        details["cot_progress"] = {
            key: value
            for key, value in cot_progress.items()
            if key != "evaluations"
        }
        details["cot_evaluations"] = cot_progress["evaluations"]
        row["cot_evaluated_count"] = cot_progress["completed"]
        row["cot_pending_count"] = cot_progress["total"] - cot_progress["completed"]
        if cot_progress["complete"]:
            cot_metrics = cot_reliability_metrics(cot_progress["evaluations"])
            row["ACC_FC_MCoT (%)"] = percentage(cot_metrics["ACC_FC_MCoT"])
            row["VHR_CoT (%)"] = percentage(cot_metrics["VHR_CoT"])
            row["LHR_CoT (%)"] = percentage(cot_metrics["LHR_CoT"])
            row["cot_status"] = "complete"
        else:
            row["cot_status"] = "cached_incomplete" if skip_cot_api else "incomplete"

    return row, details


GRADING_FIELDS = [
    "task",
    "model",
    "prompt_setting",
    "expected_count",
    "result_count",
    "parsed_count",
    "missing_count",
    "unparsed_count",
    "ACC (%)",
    "MP (%)",
    "MR (%)",
    "MF1 (%)",
    "NMAE (%)",
    "R_K (%)",
    "over_grading_rate (%)",
    "under_grading_rate (%)",
    "grading_status",
]

COT_RECORD_FIELDS = [
    "task",
    "objective_image",
    "result_path",
    "judge_model",
    "J",
    "B",
    "F",
    "V",
    "L",
    "V_H",
    "L_H",
    "first_error_type",
    "error_step",
    "judge_reason",
    "fully_correct",
]


def select_fields(row, fields):
    return {field: row[field] for field in fields}


def cot_record_rows(task):
    rows = []
    for path in sorted(cot_metrics_dir(task).glob("test_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        evaluation = data["evaluation"]
        row = {
            "task": data["task"],
            "objective_image": data["objective_image"],
            "result_path": data["result_path"],
            "judge_model": data["judge_model"],
        }
        row.update(
            {
                field: evaluation[field]
                for field in COT_RECORD_FIELDS
                if field in evaluation
            }
        )
        rows.append(select_fields(row, COT_RECORD_FIELDS))
    return rows


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def grading_details_output(details):
    shared = {
        key: details.get(key)
        for key in (
            "task",
            "model",
            "recorded_models",
            "result_directory",
        )
    }
    return {
        **shared,
        "missing_results": details.get("missing_results", []),
        "unparsed_results": details.get("unparsed_results", []),
        "grading": details.get("grading"),
    }


def main():
    args = parse_args()
    judge_client = None if args.skip_cot_api else commercial_mllm_client()

    for task in args.tasks:
        cot_dir = cot_metrics_dir(task)
        if not args.skip_cot_api:
            cot_dir.mkdir(parents=True, exist_ok=True)
        row, task_details = calculate_task(
            task,
            args.result_model_name,
            args.skip_cot_api,
            judge_client,
            JUDGE_SETTINGS,
            args.cot_limit,
        )
        grading_details = grading_details_output(task_details)

        grading_dir = grading_metrics_dir(task)
        grading_dir.mkdir(parents=True, exist_ok=True)
        grading_csv_path = grading_dir / "Grading_Metrics.csv"
        grading_details_path = grading_dir / "Grading_Metrics_Details.json"
        write_csv(grading_csv_path, [select_fields(row, GRADING_FIELDS)])
        grading_details_path.write_text(
            json.dumps({task: grading_details}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        print(
            f"{task}: results={row['result_count']}/{row['expected_count']}, "
            f"parsed={row['parsed_count']}, grading={row['grading_status']}"
        )
        print(f"Grading metrics: {grading_csv_path}")
        if not args.skip_cot_api and not args.cot_json_only:
            cot_csv_path = cot_dir / "CoT_Evaluation_Records.csv"
            if row["cot_status"] == "complete":
                write_csv(cot_csv_path, cot_record_rows(task))
                legacy_csv_path = cot_dir / "CoT_Reliability_Metrics.csv"
                if legacy_csv_path.is_file():
                    try:
                        legacy_csv_path.unlink()
                    except PermissionError:
                        print(
                            "Close CoT_Reliability_Metrics.csv so it can be removed."
                        )
                print(f"CoT evaluation records: {cot_csv_path}")
            else:
                if cot_csv_path.is_file():
                    try:
                        cot_csv_path.unlink()
                    except PermissionError:
                        print(
                            "Close the existing CoT metrics CSV so it can be removed."
                        )
                print(
                    "CoT evaluation is incomplete; summary metrics were not generated."
                )
        elif args.cot_json_only:
            for csv_name in (
                "CoT_Evaluation_Records.csv",
                "CoT_Reliability_Metrics.csv",
            ):
                cot_csv_path = cot_dir / csv_name
                if cot_csv_path.is_file():
                    try:
                        cot_csv_path.unlink()
                    except PermissionError:
                        print(
                            f"Close {csv_name} so it can be removed."
                        )
            print("Per-image CoT JSON files were generated without summary metrics.")


if __name__ == "__main__":
    main()

