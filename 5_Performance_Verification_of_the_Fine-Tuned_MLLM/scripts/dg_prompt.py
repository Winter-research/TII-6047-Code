import base64
import json


def encode_image(path):
    return base64.b64encode(path.read_bytes()).decode("ascii")


def system_message(text):
    return {"role": "system", "content": text}


def user_text_message(text):
    return {"role": "user", "content": text}


def user_image_message(text, image_path):
    return {
        "role": "user",
        "content": text,
        "images": [encode_image(image_path)],
    }


def reference_answer(example):
    article = "an" if example["grade"] in {"Else", "Urgent"} else "a"
    return (
        f'This is a reference image classified as {article} "{example["grade"]}" grade. '
        "Here is the result in JSON format:\n"
        + json.dumps(example["data"], ensure_ascii=False, indent=2)
    )


def task1_reference_messages(examples, header):
    if len(examples) != 4:
        raise ValueError(f"Task1 requires 4 reference examples, received {len(examples)}")
    return [
        user_text_message(header),
        user_image_message("Example 1:", examples[0]["image_path"]),
        user_text_message(reference_answer(examples[0])),
        user_image_message("Example 2:", examples[1]["image_path"]),
        user_text_message(reference_answer(examples[1])),
        user_image_message("Example 3:", examples[2]["image_path"]),
        user_text_message(reference_answer(examples[2])),
        user_image_message("Example 4:", examples[3]["image_path"]),
        user_text_message(reference_answer(examples[3])),
    ]


def task2_reference_messages(examples, header):
    if len(examples) != 3:
        raise ValueError(f"Task2 requires 3 reference examples, received {len(examples)}")
    return [
        user_text_message(header),
        user_image_message("Example 1:", examples[0]["image_path"]),
        user_text_message(reference_answer(examples[0])),
        user_image_message("Example 2:", examples[1]["image_path"]),
        user_text_message(reference_answer(examples[1])),
        user_image_message("Example 3:", examples[2]["image_path"]),
        user_text_message(reference_answer(examples[2])),
    ]


def task3_reference_messages(examples, header):
    if len(examples) != 4:
        raise ValueError(f"Task3 requires 4 reference examples, received {len(examples)}")
    return [
        user_text_message(header),
        user_image_message("Example 1:", examples[0]["image_path"]),
        user_text_message(reference_answer(examples[0])),
        user_image_message("Example 2:", examples[1]["image_path"]),
        user_text_message(reference_answer(examples[1])),
        user_image_message("Example 3:", examples[2]["image_path"]),
        user_text_message(reference_answer(examples[2])),
        user_image_message("Example 4:", examples[3]["image_path"]),
        user_text_message(reference_answer(examples[3])),
    ]


def reference_messages(task_name, examples, header):
    if task_name == "Task1":
        return task1_reference_messages(examples, header)
    if task_name == "Task2":
        return task2_reference_messages(examples, header)
    if task_name == "Task3":
        return task3_reference_messages(examples, header)
    raise ValueError(f"Unsupported task: {task_name}")


def build_messages(task_name, components, examples, target_image):
    return [
        system_message(components["role"]),
        user_text_message(components["task"]),
        user_text_message(components["decision_tree"]),
        user_text_message(components["format"]),
        *reference_messages(task_name, examples, components["reference"]),
        user_image_message(components["objective"], target_image),
        user_text_message(components["objective_instruction"]),
        user_text_message(components["question_4"]),
    ]


def render_prompt_text(messages):
    system_parts = []
    user_parts = []

    for message in messages:
        parts = [message["content"]]
        if message.get("images"):
            parts.append("<image>")
        if message["role"] == "system":
            system_parts.extend(parts)
        elif message["role"] == "user":
            user_parts.extend(parts)

    return (
        "[System Prompt]\n"
        + "\n\n".join(system_parts)
        + "\n\n[User Prompt]\n"
        + "\n\n".join(user_parts)
        + "\n"
    )
