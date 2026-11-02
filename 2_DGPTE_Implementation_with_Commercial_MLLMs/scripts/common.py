import base64
import json
import os
import sys
import time
from pathlib import Path

import yaml


SECTION_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = SECTION_DIR.parent
CONFIG_DIR = SECTION_DIR / "configs"
RESULTS_DIR = SECTION_DIR / "results"


def load_env_file(path):
    path = Path(path)
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name:
            os.environ.setdefault(name, value)


load_env_file(SECTION_DIR / ".env")


def load_yaml(path):
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML configuration: {path}")
    return data


def load_model_config():
    return load_yaml(CONFIG_DIR / "commercial_model.yaml")


def load_tasks_config():
    return load_yaml(CONFIG_DIR / "tasks.yaml")


def load_task(task_name):
    config = load_tasks_config()
    try:
        task = dict(config["tasks"][task_name])
    except KeyError as error:
        raise ValueError(f"Unknown task: {task_name}") from error

    task["task_name"] = task_name
    task["dataset_dir"] = PROJECT_DIR / task["dataset_dir"]
    task["image_dir"] = PROJECT_DIR / task["image_dir"]
    task["allowed_grades"] = set(task["allowed_grades"])
    task["required_fields"] = set(task["required_fields"])
    return task


def load_prompt_components(task_name):
    project_path = str(PROJECT_DIR)
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
    from Prompt_Components import load_components

    return load_components(task_name)


def runtime_settings():
    config = load_model_config()
    return {
        "model": config["model"]["name"],
        "resolution": int(config["image"]["resolution"]),
        "max_retries": int(config["request"]["max_retries"]),
        "retry_delay_seconds": float(config["request"]["retry_delay_seconds"]),
        "performance_temperature": float(config["performance_testing"]["temperature"]),
        "annotation_temperature": float(config["automatic_annotation"]["temperature"]),
    }


def api_credentials():
    api_key = os.environ.get("COMMERCIAL_MLLM_API_KEY", "").strip()
    base_url = os.environ.get("COMMERCIAL_MLLM_BASE_URL", "").strip()
    if not api_key or not base_url:
        raise RuntimeError(
            "Set COMMERCIAL_MLLM_API_KEY and COMMERCIAL_MLLM_BASE_URL before running API requests."
        )
    return api_key, base_url


def create_client():
    from openai import OpenAI

    api_key, base_url = api_credentials()
    return OpenAI(api_key=api_key, base_url=base_url)


def model_slug(model):
    return model.replace("/", "_").replace("\\", "_")


def image_data_url(path):
    path = Path(path)
    mime_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def text_item(text):
    return {"type": "text", "text": text}


def image_item(path):
    return {"type": "image_url", "image_url": {"url": image_data_url(path)}}


def append_text(content, *parts):
    text = "\n\n".join(part for part in parts if part)
    if text:
        content.append(text_item(text))


def append_prompt_with_images(content, prompt_text, image_paths):
    segments = prompt_text.split("<image>")
    if len(segments) - 1 != len(image_paths):
        raise ValueError("Reference image placeholder count does not match image count")

    for index, segment in enumerate(segments):
        if segment.strip():
            content.append(text_item(segment.strip()))
        if index < len(image_paths):
            content.append(image_item(image_paths[index]))


def prompt_text(messages):
    sections = []
    for message in messages:
        role = message["role"]
        content = message["content"]
        if isinstance(content, str):
            rendered = content
        else:
            parts = []
            for item in content:
                if item["type"] == "text":
                    parts.append(item["text"])
                elif item["type"] == "image_url":
                    parts.append("<image>")
            rendered = "\n\n".join(parts)
        sections.append((role, rendered))

    system_text = "\n\n".join(text for role, text in sections if role == "system")
    user_text = "\n\n".join(text for role, text in sections if role == "user")
    return f"[System Prompt]\n{system_text}\n\n[User Prompt]\n{user_text}\n"


def call_with_retries(operation, max_retries, retry_delay_seconds):
    for attempt in range(1, max_retries + 1):
        try:
            return operation()
        except Exception as error:
            if attempt == max_retries:
                raise
            print(f"Attempt {attempt}/{max_retries} failed: {error}")
            time.sleep(retry_delay_seconds)


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def project_relative(path):
    return Path(path).resolve().relative_to(PROJECT_DIR.resolve()).as_posix()
