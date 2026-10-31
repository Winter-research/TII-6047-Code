import json
import os
import sys
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
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML configuration: {path}")
    return data


def load_model_config():
    return load_yaml(CONFIG_DIR / "ollama_model.yaml")


def load_task(task_name):
    config = load_yaml(CONFIG_DIR / "tasks.yaml")
    try:
        task = dict(config["tasks"][task_name])
    except KeyError as error:
        raise ValueError(f"Unknown task: {task_name}") from error

    task["task_name"] = task_name
    task["dataset_dir"] = PROJECT_DIR / task["dataset_dir"]
    task["grade_map"] = dict(config["grade_map"])
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
        "ollama_url": config["ollama"]["api_url"],
        "model": config["ollama"]["model"],
        "result_model_name": config["result"]["model_name"],
        "resolution": int(config["image"]["resolution"]),
        "temperature": float(config["generation"]["temperature"]),
        "top_p": float(config["generation"]["top_p"]),
        "num_predict": int(config["generation"]["num_predict"]),
        "num_ctx": int(config["generation"]["num_ctx"]),
        "timeout": int(config["request"]["timeout_seconds"]),
        "max_retries": int(config["request"]["max_retries"]),
        "retry_delay": float(config["request"]["retry_delay_seconds"]),
    }


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def project_relative(path):
    return Path(path).resolve().relative_to(PROJECT_DIR.resolve()).as_posix()
