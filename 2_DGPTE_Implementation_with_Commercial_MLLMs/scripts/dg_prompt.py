import json

from common import image_item, text_item


def system_message(role_prompt):
    return {"role": "system", "content": role_prompt}


def user_text_message(text):
    return {"role": "user", "content": [text_item(text)]}


def user_image_message(image_path):
    return {"role": "user", "content": [image_item(image_path)]}


def reference_answer(example, include_reasoning):
    article = "an" if example["grade"] in {"Else", "Urgent"} else "a"
    if include_reasoning:
        return (
            f'This is a reference image classified as {article} "{example["grade"]}" grade. '
            "Here is the result in JSON format:\n"
            + json.dumps(example["data"], ensure_ascii=False, indent=2)
        )
    return (
        f'This reference image is classified as {article} '
        f'"{example["grade"]}" grade.'
    )


def task1_reference_messages(examples, include_reasoning, header):
    if len(examples) != 4:
        raise ValueError(f"Task1 requires 4 reference examples, received {len(examples)}")

    answer_1 = reference_answer(examples[0], include_reasoning)
    answer_2 = reference_answer(examples[1], include_reasoning)
    answer_3 = reference_answer(examples[2], include_reasoning)
    answer_4 = reference_answer(examples[3], include_reasoning)

    return [
        user_text_message(header),
        user_text_message("Example 1:"),
        user_image_message(examples[0]["image_path"]),
        user_text_message(answer_1),
        user_text_message("Example 2:"),
        user_image_message(examples[1]["image_path"]),
        user_text_message(answer_2),
        user_text_message("Example 3:"),
        user_image_message(examples[2]["image_path"]),
        user_text_message(answer_3),
        user_text_message("Example 4:"),
        user_image_message(examples[3]["image_path"]),
        user_text_message(answer_4),
    ]


def task2_reference_messages(examples, include_reasoning, header):
    if len(examples) != 3:
        raise ValueError(f"Task2 requires 3 reference examples, received {len(examples)}")

    answer_1 = reference_answer(examples[0], include_reasoning)
    answer_2 = reference_answer(examples[1], include_reasoning)
    answer_3 = reference_answer(examples[2], include_reasoning)

    return [
        user_text_message(header),
        user_text_message("Example 1:"),
        user_image_message(examples[0]["image_path"]),
        user_text_message(answer_1),
        user_text_message("Example 2:"),
        user_image_message(examples[1]["image_path"]),
        user_text_message(answer_2),
        user_text_message("Example 3:"),
        user_image_message(examples[2]["image_path"]),
        user_text_message(answer_3),
    ]


def task3_reference_messages(examples, include_reasoning, header):
    if len(examples) != 4:
        raise ValueError(f"Task3 requires 4 reference examples, received {len(examples)}")

    answer_1 = reference_answer(examples[0], include_reasoning)
    answer_2 = reference_answer(examples[1], include_reasoning)
    answer_3 = reference_answer(examples[2], include_reasoning)
    answer_4 = reference_answer(examples[3], include_reasoning)

    return [
        user_text_message(header),
        user_text_message("Example 1:"),
        user_image_message(examples[0]["image_path"]),
        user_text_message(answer_1),
        user_text_message("Example 2:"),
        user_image_message(examples[1]["image_path"]),
        user_text_message(answer_2),
        user_text_message("Example 3:"),
        user_image_message(examples[2]["image_path"]),
        user_text_message(answer_3),
        user_text_message("Example 4:"),
        user_image_message(examples[3]["image_path"]),
        user_text_message(answer_4),
    ]


def reference_messages(task_name, examples, include_reasoning, header):
    if task_name == "Task1":
        return task1_reference_messages(examples, include_reasoning, header)
    if task_name == "Task2":
        return task2_reference_messages(examples, include_reasoning, header)
    if task_name == "Task3":
        return task3_reference_messages(examples, include_reasoning, header)
    raise ValueError(f"Unsupported task: {task_name}")


def build_performance_messages(task_name, prompt_number, target_image, prompts, examples):
    role_prompt = prompts["role"]                    # P_R
    task_prompt = prompts["task"]                    # P_T
    decision_tree_prompt = prompts["decision_tree"]  # P_DT
    output_format_prompt = prompts["format"]         # P_F
    objective_image_prompt = prompts["objective"]    # P_OI

    if prompt_number == 1:
        # P_R + P_T + P_OI + Objective Image + P_Q1-1
        return [
            system_message(role_prompt),
            user_text_message(task_prompt),
            user_text_message(objective_image_prompt),
            user_image_message(target_image),
            user_text_message(prompts["question_1"]),
        ]

    if prompt_number == 2:
        # P_R + P_T + P_DT + P_F + P_OI + Objective Image + P_Q1-2
        return [
            system_message(role_prompt),
            user_text_message(task_prompt),
            user_text_message(decision_tree_prompt),
            user_text_message(output_format_prompt),
            user_text_message(objective_image_prompt),
            user_image_message(target_image),
            user_text_message(prompts["objective_instruction"]),
            user_text_message(prompts["question_2"]),
        ]

    if prompt_number == 3:
        # P_R + P_T + P_RI (result only) + P_OI + Objective Image + P_Q1-3
        return [
            system_message(role_prompt),
            user_text_message(task_prompt),
            *reference_messages(
                task_name,
                examples,
                include_reasoning=False,
                header=prompts["reference_result_only"],
            ),
            user_text_message(objective_image_prompt),
            user_image_message(target_image),
            user_text_message(prompts["question_3"]),
        ]

    if prompt_number == 4:
        # P_R + P_T + P_DT + P_F + P_RI (CoT) + P_OI + Objective Image + P_Q1-4
        return [
            system_message(role_prompt),
            user_text_message(task_prompt),
            user_text_message(decision_tree_prompt),
            user_text_message(output_format_prompt),
            *reference_messages(
                task_name,
                examples,
                include_reasoning=True,
                header=prompts["reference"],
            ),
            user_text_message(objective_image_prompt),
            user_image_message(target_image),
            user_text_message(prompts["objective_instruction"]),
            user_text_message(prompts["question_4"]),
        ]

    raise ValueError(f"Unsupported prompt number: {prompt_number}")
