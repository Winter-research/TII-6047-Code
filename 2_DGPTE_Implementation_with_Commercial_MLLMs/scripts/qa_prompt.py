from dg_prompt import (
    system_message,
    task1_reference_messages,
    task2_reference_messages,
    task3_reference_messages,
    user_image_message,
    user_text_message,
)


def build_task1_qa_messages(target_image, ground_truth, prompts, examples):
    return [
        system_message(prompts["role"]),
        user_text_message(prompts["task"]),
        user_text_message(prompts["decision_tree"]),
        user_text_message(prompts["format"]),
        *task1_reference_messages(examples, include_reasoning=True, header=prompts["reference"]),
        user_text_message(prompts["objective"]),
        user_image_message(target_image),
        user_text_message(prompts["objective_instruction"]),
        user_text_message(prompts["ground_truth"].format(ground_truth=ground_truth)),
        user_text_message(prompts["annotation_question"]),
    ]


def build_task2_qa_messages(target_image, ground_truth, prompts, examples):
    return [
        system_message(prompts["role"]),
        user_text_message(prompts["task"]),
        user_text_message(prompts["decision_tree"]),
        user_text_message(prompts["format"]),
        *task2_reference_messages(examples, include_reasoning=True, header=prompts["reference"]),
        user_text_message(prompts["objective"]),
        user_image_message(target_image),
        user_text_message(prompts["objective_instruction"]),
        user_text_message(prompts["ground_truth"].format(ground_truth=ground_truth)),
        user_text_message(prompts["annotation_question"]),
    ]


def build_task3_qa_messages(target_image, ground_truth, prompts, examples):
    return [
        system_message(prompts["role"]),
        user_text_message(prompts["task"]),
        user_text_message(prompts["decision_tree"]),
        user_text_message(prompts["format"]),
        *task3_reference_messages(examples, include_reasoning=True, header=prompts["reference"]),
        user_text_message(prompts["objective"]),
        user_image_message(target_image),
        user_text_message(prompts["objective_instruction"]),
        user_text_message(prompts["ground_truth"].format(ground_truth=ground_truth)),
        user_text_message(prompts["annotation_question"]),
    ]


def build_qa_messages(task_name, target_image, ground_truth, prompts, examples):
    if task_name == "Task1":
        return build_task1_qa_messages(target_image, ground_truth, prompts, examples)
    if task_name == "Task2":
        return build_task2_qa_messages(target_image, ground_truth, prompts, examples)
    if task_name == "Task3":
        return build_task3_qa_messages(target_image, ground_truth, prompts, examples)
    raise ValueError(f"Unsupported task: {task_name}")
