import argparse
import json
import re
import time

import requests

from common import (
    RESULTS_DIR,
    load_prompt_components,
    load_task,
    project_relative,
    runtime_settings,
    write_json,
)
from dg_prompt import build_messages, render_prompt_text


TASK_NAMES = ("Task1", "Task2", "Task3")
PROMPT_SETTING = "Prompt 4 - GDT-Based CoT Process + Reference Images"
ENGLISH_TO_CHINESE_GRADE = {
    "Else": "其他",
    "Kind": "一般",
    "Major": "重大",
    "Urgent": "紧急",
}


def normalize_grade(grade):
    return ENGLISH_TO_CHINESE_GRADE.get(grade, grade)
def parse_args():
    parser = argparse.ArgumentParser(description="Test the fine-tuned MLLM through Ollama.")
    parser.add_argument("--tasks", nargs="+", choices=TASK_NAMES, default=list(TASK_NAMES))
    parser.add_argument("--model")
    parser.add_argument("--ollama-url")
    parser.add_argument("--result-model-name")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_reference_examples(reference_dir, resolution):
    examples = []
    for json_path in sorted(reference_dir.glob("reference_*.json"), key=lambda path: path.name):
        image_path = reference_dir / f"{json_path.stem}_p{resolution}.jpg"
        if not image_path.is_file():
            raise FileNotFoundError(f"Missing reference image: {image_path}")
        examples.append(
            {
                "image_path": image_path,
                "data": json.loads(json_path.read_text(encoding="utf-8")),
            }
        )
    if not examples:
        raise FileNotFoundError(f"No reference JSON files found in {reference_dir}")
    return examples


def load_test_images(test_dir, resolution, limit):
    paths = sorted(test_dir.glob(f"test_*_p{resolution}.jpg"), key=lambda path: path.name)
    if not paths:
        raise FileNotFoundError(f"No test images found in {test_dir}")
    return paths[:limit] if limit > 0 else paths


def check_ollama(ollama_url, model):
    tags_url = ollama_url.rsplit("/", 1)[0] + "/tags"
    response = requests.get(tags_url, timeout=15)
    response.raise_for_status()
    models = [item.get("name", "") for item in response.json().get("models", [])]
    if model not in models:
        available = ", ".join(models) if models else "none"
        raise RuntimeError(f"Model '{model}' is unavailable. Available models: {available}")


def call_ollama(messages, settings):
    payload = {
        "model": settings["model"],
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": settings["temperature"],
            "top_p": settings["top_p"],
            "num_predict": settings["num_predict"],
            "num_ctx": settings["num_ctx"],
        },
    }

    last_error = None
    for attempt in range(1, settings["max_retries"] + 1):
        started = time.perf_counter()
        try:
            response = requests.post(
                settings["ollama_url"],
                json=payload,
                timeout=settings["timeout"],
            )
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "").strip()
            if not content:
                raise ValueError("Ollama returned an empty response")
            print(f"Ollama response received in {time.perf_counter() - started:.1f}s")
            return content
        except (requests.RequestException, ValueError, json.JSONDecodeError) as error:
            last_error = error
            if attempt == settings["max_retries"]:
                break
            print(f"Attempt {attempt}/{settings['max_retries']} failed: {error}")
            time.sleep(settings["retry_delay"])
    raise RuntimeError(f"Ollama request failed: {last_error}")


def extract_grade(response_text, allowed_grades):
    text = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        response_text.strip(),
        flags=re.IGNORECASE,
    )
    try:
        data = json.loads(text[text.index("{") : text.rindex("}") + 1])
        grade = normalize_grade(
            str(data.get("grade_result", "")).split("|", 1)[0].strip()
        )
        if grade in allowed_grades:
            return grade
    except (ValueError, json.JSONDecodeError):
        pass

    aliases = set(allowed_grades)
    aliases.update(
        english_grade
        for english_grade, chinese_grade in ENGLISH_TO_CHINESE_GRADE.items()
        if chinese_grade in allowed_grades
    )
    pattern = "|".join(sorted(map(re.escape, aliases), key=len, reverse=True))
    grades = re.findall(pattern, text)
    return normalize_grade(grades[-1]) if grades else ""


def true_grade(image_path, grade_map):
    match = re.match(r"test_(Else|Kind|Major|Urgent)_", image_path.stem)
    if not match:
        raise ValueError(f"Cannot determine true grade from {image_path.name}")
    return grade_map[match.group(1)]


def load_records(result_dir):
    records = []
    for path in result_dir.glob("test_*.json"):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return records


def result_statistics(result_dir):
    records = load_records(result_dir)
    correct = sum(int(record.get("correct", 0)) for record in records)
    return {
        "total": len(records),
        "correct": correct,
        "accuracy": correct / len(records) if records else 0.0,
    }


def run_task(task_name, args, settings):
    task = load_task(task_name)
    dataset_dir = task["dataset_dir"]
    reference_dir = dataset_dir / "Reference_dataset"
    test_dir = dataset_dir / "Test_dataset"
    components = load_prompt_components(task_name)
    examples = load_reference_examples(reference_dir, settings["resolution"])
    targets = load_test_images(test_dir, settings["resolution"], args.limit)

    prompt_dir = RESULTS_DIR / task_name / "performance_testing" / "Prompt4"
    result_dir = prompt_dir / settings["result_model_name"]
    first_messages = build_messages(task_name, components, examples, targets[0])
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / "prompt.txt").write_text(
        render_prompt_text(first_messages),
        encoding="utf-8",
    )

    print(f"\n=== {task_name} ===")
    print(f"Model: {settings['model']}")
    print(f"Ollama API: {settings['ollama_url']}")
    print(f"Test images: {len(targets)}")
    print(f"Output directory: {result_dir}")

    if args.dry_run:
        print("Prompt built successfully. No Ollama request was sent.")
        return None

    result_dir.mkdir(parents=True, exist_ok=True)
    completed = {record.get("picture") for record in load_records(result_dir)}

    for index, target_image in enumerate(targets, start=1):
        if target_image.name in completed and not args.overwrite:
            print(f"[{index}/{len(targets)}] Skipped: {target_image.name}")
            continue

        print(f"[{index}/{len(targets)}] Processing: {target_image.name}")
        try:
            messages = build_messages(task_name, components, examples, target_image)
            response_text = call_ollama(messages, settings)
            expected = true_grade(target_image, task["grade_map"])
            predicted = extract_grade(response_text, set(task["grade_map"].values()))
            write_json(
                result_dir / f"{target_image.stem}.json",
                {
                    "picture": target_image.name,
                    "image_path": project_relative(target_image),
                    "true_grade": expected,
                    "response": response_text,
                    "answer": predicted,
                    "correct": int(predicted == expected),
                    "model": settings["result_model_name"],
                    "runtime_model": settings["model"],
                    "prompt_setting": PROMPT_SETTING,
                },
            )
            print(f"Answer: {predicted or 'unparsed'} | True: {expected}")
        except Exception as error:
            print(f"Failed: {target_image.name} | {error}")

    statistics = result_statistics(result_dir)
    print(
        f"Completed {task_name}: {statistics['correct']}/{statistics['total']} "
        f"({statistics['accuracy']:.2%})"
    )
    return statistics


def main():
    args = parse_args()
    settings = runtime_settings()
    if args.model:
        settings["model"] = args.model
    if args.ollama_url:
        settings["ollama_url"] = args.ollama_url
    if args.result_model_name:
        settings["result_model_name"] = args.result_model_name

    if not args.dry_run:
        check_ollama(settings["ollama_url"], settings["model"])

    task_statistics = []
    for task_name in args.tasks:
        statistics = run_task(task_name, args, settings)
        if statistics is not None:
            task_statistics.append(statistics)

    if task_statistics:
        total = sum(statistics["total"] for statistics in task_statistics)
        correct = sum(statistics["correct"] for statistics in task_statistics)
        print(f"All selected tasks: {correct}/{total} ({correct / total if total else 0:.2%})")


if __name__ == "__main__":
    main()
