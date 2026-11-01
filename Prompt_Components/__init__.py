"""Shared prompt-component library for Task1, Task2, and Task3."""

from importlib import import_module


TASK_NAMES = ("Task1", "Task2", "Task3")


def load_components(task_name):
    """Return a copy of the prompt components for one task."""
    if task_name not in TASK_NAMES:
        raise ValueError(f"Unsupported task: {task_name}")
    module = import_module(f"{__name__}.{task_name}")
    return dict(module.COMPONENTS)
