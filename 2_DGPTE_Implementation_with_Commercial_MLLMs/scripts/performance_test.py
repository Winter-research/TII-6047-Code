import argparse
import json
import re
from pathlib import Path

from common import (
    RESULTS_DIR,
    call_with_retries,
    create_client,
    load_prompt_components,
    load_task,
    model_slug,
    project_relative,
    prompt_text,
    runtime_settings,
    write_json,
)
from dg_prompt import build_performance_messages


PROMPT_NAMES = {
    1: "Prompt 1 - Only Result",
    2: "Prompt 2 - GDT-Based CoT Process",
    3: "Prompt 3 - Only Result + Reference Images",
    4: "Prompt 4 - GDT-Based CoT Process + Reference Images",
}

def load_reference_examples(reference_dir, reference_image_dir, resolution, allowed_grades):
    examples = []
    for json_path in sorted(reference_dir.glob("reference_*.json"), key=lambda path: path.name):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        source_grade = str(data.get("grade_result", "")).split("|", 1)[0].strip()
        grade = source_grade
        if grade not in allowed_grades:
            raise ValueError(f"Invalid grade_result in {json_path}: {source_grade}")

        image_path = reference_image_dir / f"{json_path.stem}_p{resolution}.jpg"
        if not image_path.is_file():
            raise FileNotFoundError(f"Missing reference image: {image_path}")
        examples.append(
            {
                "image_path": image_path,
                "data": data,
                "grade": grade,
            }
        )

    if not examples:
        raise FileNotFoundError(f"No reference JSON files found in {reference_dir}")
    return examples


def extract_grade(response_text, allowed_grades):
    text = response_text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)

    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        data = json.loads(text[start:end])
        grade = str(data.get("grade_result", "")).split("|", 1)[0].strip()
        if grade in allowed_grades:
            return grade
    except (ValueError, json.JSONDecodeError):
        pass

    allowed_pattern = "|".join(
        sorted(map(re.escape, allowed_grades), key=len, reverse=True)
    )
    marked = re.findall(
        rf"(?:\*\*\*|###)\s*({allowed_pattern})\s*(?:\*\*\*|###)",
        text,
    )
    if marked:
        return marked[-1]
    grades = re.findall(allowed_pattern, text)
    return grades[-1] if grades else ""


def true_grade(path):
    match = re.match(r"test_(Else|Kind|Major|Urgent)_", path.stem)
    if not match:
        raise ValueError(f"Cannot determine true grade from filename: {path.name}")
    return match.group(1)


def existing_records(result_dir):
    records = []
    for path in result_dir.glob("test_*.json"):
        if path.stem.endswith("_zh"):
            continue
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return records


def result_statistics(result_dir):
    records = existing_records(result_dir)
    correct = sum(int(record.get("correct", 0)) for record in records)
    total = len(records)
    return {
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total else 0.0,
    }


def run(args):
    task = load_task(args.task)
    settings = runtime_settings()
    resolution = settings["resolution"]
    dataset_dir = task["dataset_dir"]
    image_dir = task["image_dir"]
    reference_dir = dataset_dir / "Reference_dataset"
    reference_image_dir = image_dir / "Reference_dataset"
    test_dir = image_dir / "Test_dataset"

    prompts = load_prompt_components(args.task)
    examples = load_reference_examples(
        reference_dir, reference_image_dir, resolution, task["allowed_grades"]
    )
    targets = sorted(test_dir.glob(f"test_*_p{resolution}.jpg"), key=lambda path: path.name)
    if not targets:
        raise FileNotFoundError(f"No test images found in {test_dir}")
    if args.limit is not None:
        targets = targets[: args.limit]

    prompt_dir = RESULTS_DIR / "performance_testing" / args.task / f"Prompt{args.prompt}"
    result_dir = prompt_dir / model_slug(settings["model"])
    result_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / "prompt.txt").write_text(
        prompt_text(
            build_performance_messages(
                args.task,
                args.prompt,
                targets[0],
                prompts,
                examples,
            )
        ),
        encoding="utf-8",
    )

    if args.dry_run:
        print(f"Prompt built successfully: {prompt_dir / 'prompt.txt'}")
        return

    client = create_client()
    completed = 0
    for index, target_image in enumerate(targets, start=1):
        output_path = result_dir / f"{target_image.stem}.json"
        if output_path.is_file() and not args.overwrite:
            print(f"[{index}/{len(targets)}] Skipped: {target_image.name}")
            continue

        messages = build_performance_messages(
            args.task,
            args.prompt,
            target_image,
            prompts,
            examples,
        )

        def request():
            response = client.chat.completions.create(
                model=settings["model"],
                messages=messages,
                stream=False,
                temperature=settings["performance_temperature"],
            )
            return response.choices[0].message.content

        response_text = call_with_retries(
            request,
            settings["max_retries"],
            settings["retry_delay_seconds"],
        )
        expected = true_grade(target_image)
        predicted = extract_grade(response_text, task["allowed_grades"])
        record = {
            "picture": target_image.name,
            "image_path": project_relative(target_image),
            "true_grade": expected,
            "response": response_text,
            "answer": predicted,
            "correct": int(predicted == expected),
            "model": settings["model"],
            "prompt": args.prompt,
            "prompt_setting": PROMPT_NAMES[args.prompt],
        }
        write_json(output_path, record)
        completed += 1
        print(f"[{index}/{len(targets)}] {target_image.name}: {predicted or 'unparsed'}")

    statistics = result_statistics(result_dir)
    print(
        f"Completed: {completed}; accuracy: "
        f"{statistics['correct']}/{statistics['total']} "
        f"({statistics['accuracy']:.2%})"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Run commercial-MLLM performance testing.")
    parser.add_argument("--task", required=True, choices=["Task1", "Task2", "Task3"])
    parser.add_argument("--prompt", required=True, type=int, choices=[1, 2, 3, 4])
    parser.add_argument("--limit", type=int, help="Process only the first N samples.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing results.")
    parser.add_argument("--dry-run", action="store_true", help="Build the prompt without an API call.")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
