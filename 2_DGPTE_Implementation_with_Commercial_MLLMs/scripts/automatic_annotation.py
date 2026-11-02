import argparse
import json
import re

from common import (
    RESULTS_DIR,
    call_with_retries,
    create_client,
    load_prompt_components,
    load_task,
    model_slug,
    prompt_text,
    runtime_settings,
    write_json,
)
from qa_prompt import build_qa_messages


def load_reference_examples(reference_dir, reference_image_dir, resolution):
    examples = []
    for json_path in sorted(reference_dir.glob("reference_*.json"), key=lambda path: path.name):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        grade = str(data.get("grade_result", "")).split("|", 1)[0].strip()
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


def ground_truth(json_path, allowed_grades):
    data = json.loads(json_path.read_text(encoding="utf-8"))
    grade = str(data.get("grade_result", "")).split("|", 1)[0].strip()
    if grade not in allowed_grades:
        raise ValueError(f"Invalid grade_result in {json_path}: {grade}")
    return grade


def target_image(train_dir, json_path, resolution):
    path = train_dir / f"{json_path.stem}_p{resolution}.jpg"
    if not path.is_file():
        raise FileNotFoundError(f"Missing target image: {path}")
    return path


def parse_annotation(response_text):
    text = response_text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    return json.loads(text)


def validate_annotation(annotation, required_fields, expected_grade):
    if set(annotation) != required_fields:
        raise ValueError(
            f"Invalid annotation fields: expected {sorted(required_fields)}, "
            f"received {sorted(annotation)}"
        )
    annotated_grade = str(annotation["grade_result"]).split("|", 1)[0].strip()
    if annotated_grade != expected_grade:
        raise ValueError(
            f"Generated grade {annotated_grade!r} does not match "
            f"ground truth {expected_grade!r}"
        )
    return annotation


def run(args):
    task = load_task(args.task)
    settings = runtime_settings()
    resolution = settings["resolution"]
    dataset_dir = task["dataset_dir"]
    image_dir = task["image_dir"]
    reference_dir = dataset_dir / "Reference_dataset"
    train_dir = dataset_dir / "Train_dataset"
    reference_image_dir = image_dir / "Reference_dataset"
    train_image_dir = image_dir / "Train_dataset"
    prompts = load_prompt_components(args.task)
    examples = load_reference_examples(reference_dir, reference_image_dir, resolution)
    train_json_paths = sorted(train_dir.glob("train_*.json"), key=lambda path: path.name)
    if not train_json_paths:
        raise FileNotFoundError(f"No training JSON files found in {train_dir}")
    if args.limit is not None:
        train_json_paths = train_json_paths[: args.limit]

    task_result_dir = RESULTS_DIR / "automatic_annotation" / args.task
    result_dir = task_result_dir / model_slug(settings["model"])
    result_dir.mkdir(parents=True, exist_ok=True)

    first_path = train_json_paths[0]
    first_messages = build_qa_messages(
        args.task,
        target_image(train_image_dir, first_path, resolution),
        ground_truth(first_path, task["allowed_grades"]),
        prompts,
        examples,
    )
    (task_result_dir / "prompt.txt").write_text(
        prompt_text(first_messages),
        encoding="utf-8",
    )

    if args.dry_run:
        print(f"Prompt built successfully: {task_result_dir / 'prompt.txt'}")
        return

    client = create_client()
    completed = 0
    for index, json_path in enumerate(train_json_paths, start=1):
        output_path = result_dir / json_path.name
        if output_path.is_file() and not args.overwrite:
            print(f"[{index}/{len(train_json_paths)}] Skipped: {json_path.name}")
            continue

        expected_grade = ground_truth(json_path, task["allowed_grades"])
        messages = build_qa_messages(
            args.task,
            target_image(train_image_dir, json_path, resolution),
            expected_grade,
            prompts,
            examples,
        )

        def request_and_validate():
            response = client.chat.completions.create(
                model=settings["model"],
                messages=messages,
                stream=False,
                temperature=settings["annotation_temperature"],
                response_format={"type": "json_object"},
            )
            annotation = parse_annotation(response.choices[0].message.content)
            return validate_annotation(
                annotation,
                task["required_fields"],
                expected_grade,
            )

        annotation = call_with_retries(
            request_and_validate,
            settings["max_retries"],
            settings["retry_delay_seconds"],
        )
        write_json(output_path, annotation)
        completed += 1
        print(f"[{index}/{len(train_json_paths)}] Generated: {output_path.name}")

    print(f"Completed: {completed}; output directory: {result_dir}")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate commercial-MLLM annotations.")
    parser.add_argument("--task", required=True, choices=["Task1", "Task2", "Task3"])
    parser.add_argument("--limit", type=int, help="Process only the first N samples.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing results.")
    parser.add_argument("--dry-run", action="store_true", help="Build the prompt without an API call.")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
