import json
import random
import sys
from pathlib import Path

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
SECTION_DIR = SCRIPT_DIR.parent
PROJECT_DIR = SECTION_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from Prompt_Components import load_components

CONFIG_PATH = SECTION_DIR / "configs" / "dataset_construction.yaml"
CONFIG = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))

RESOLUTION = int(CONFIG["resolution"])
RANDOM_SEED = int(CONFIG["random_seed"])
SAMPLE_DATASET_DIR = PROJECT_DIR / CONFIG["sample_dataset_dir"]
PROCESSED_IMAGES_DIR = PROJECT_DIR / CONFIG["processed_images_dir"]
OUTPUT_DIRS = tuple(PROJECT_DIR / path for path in CONFIG["output_dirs"])
TASKS = tuple(
    {
        "name": name,
        "output": task["output"],
    }
    for name, task in CONFIG["tasks"].items()
)
MULTI_TASK_OUTPUT = CONFIG["multi_task_output"]


def load_json_text(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(data, ensure_ascii=False, indent=2)


def build_reference_prompt(json_paths):
    lines = [
        f"[Reference Images] Here are {len(json_paths)} manually verified reference images "
        "with their complete grading processes and results. Please study and reference "
        "the reasoning method and output format."
    ]
    for index, json_path in enumerate(json_paths, start=1):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        grade = str(data.get("grade_result", "")).split("|", 1)[0].strip()
        article = "an" if grade in {"Else", "Urgent"} else "a"
        lines.extend(["", f"Example {index}:", "<image>"])
        lines.append(
            f'This is a reference image classified as {article} "{grade}" grade. '
            "Here is the result in JSON format:"
        )
        lines.append(json.dumps(data, ensure_ascii=False, indent=2))
    return "\n".join(lines)


def resized_image_path(folder, stem):
    path = folder / f"{stem}_p{RESOLUTION}.jpg"
    if not path.is_file():
        raise FileNotFoundError(f"Missing resized image: {path}")
    return path.relative_to(PROJECT_DIR).as_posix()


def build_sample(prompts, reference_images, train_dir, json_path):
    target_image = resized_image_path(train_dir, json_path.stem)
    user_content = "\n\n".join(
        (
            prompts["task"],
            prompts["decision_tree"],
            prompts["format"],
            prompts["reference"],
            prompts["objective"],
            "<image>",
            prompts["objective_instruction"],
            prompts["question_4"],
        )
    )
    image_paths = reference_images + [target_image]

    if user_content.count("<image>") != len(image_paths):
        raise ValueError(f"Image placeholder mismatch for {json_path.name}")

    return {
        "messages": [
            {"role": "system", "content": prompts["role"]},
            {"role": "user", "content": user_content},
            {
                "role": "assistant",
                "content": "【CoT JSON Result】\n" + load_json_text(json_path),
            },
        ],
        "images": image_paths,
    }


def generate_task_dataset(task):
    dataset_dir = SAMPLE_DATASET_DIR / task["name"]
    image_dir = PROCESSED_IMAGES_DIR / task["name"]
    reference_dir = dataset_dir / "Reference_dataset"
    train_dir = dataset_dir / "Train_dataset"
    reference_image_dir = image_dir / "Reference_dataset"
    train_image_dir = image_dir / "Train_dataset"
    prompts = load_components(task["name"])

    reference_json_paths = sorted(
        reference_dir.glob("reference_*.json"), key=lambda path: path.name
    )
    train_json_paths = sorted(train_dir.glob("train_*.json"), key=lambda path: path.name)

    if not reference_json_paths:
        raise FileNotFoundError(f"No reference JSON files found in {reference_dir}")
    if not train_json_paths:
        raise FileNotFoundError(f"No training JSON files found in {train_dir}")

    prompts["reference"] = build_reference_prompt(reference_json_paths)

    reference_images = [
        resized_image_path(reference_image_dir, json_path.stem)
        for json_path in reference_json_paths
    ]
    samples = [
        build_sample(prompts, reference_images, train_image_dir, json_path)
        for json_path in train_json_paths
    ]
    random.Random(RANDOM_SEED).shuffle(samples)
    return samples


def write_dataset(samples, output_name):
    output_text = json.dumps(samples, ensure_ascii=False, indent=2)
    output_paths = []
    for output_dir in OUTPUT_DIRS:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_name
        output_path.write_text(output_text + "\n", encoding="utf-8")
        output_paths.append(output_path)
    return output_paths


def main():
    combined_samples = []

    for task in TASKS:
        samples = generate_task_dataset(task)
        output_paths = write_dataset(samples, task["output"])
        combined_samples.extend(samples)
        print(f"Generated {len(samples)} samples:")
        for output_path in output_paths:
            print(f"  {output_path}")

    random.Random(RANDOM_SEED).shuffle(combined_samples)
    output_paths = write_dataset(combined_samples, MULTI_TASK_OUTPUT)
    print(f"Generated {len(combined_samples)} samples:")
    for output_path in output_paths:
        print(f"  {output_path}")


if __name__ == "__main__":
    main()
