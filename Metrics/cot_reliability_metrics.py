import base64
import json
import re
import time
from pathlib import Path


def extract_json_object(text):
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        value = json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _field_conclusion(value):
    return str(value).split("|", 1)[0].strip()


def json_validity(model_cot, expert_cot):
    parsed = extract_json_object(model_cot)
    return int(parsed is not None and set(parsed) == set(expert_cot))


def branch_decision_correctness(model_cot, expert_cot):
    parsed = extract_json_object(model_cot)
    if parsed is None:
        return 0

    decision_fields = [
        field
        for field in expert_cot
        if field not in {"location_description", "has_nest", "grade_result"}
    ]
    return int(
        all(
            field in parsed
            and _field_conclusion(parsed[field]) == _field_conclusion(expert_cot[field])
            for field in decision_fields
        )
    )


def final_grade_correctness(model_cot, expert_cot):
    parsed = extract_json_object(model_cot)
    if parsed is None or "grade_result" not in parsed:
        return 0
    return int(
        _field_conclusion(parsed["grade_result"])
        == _field_conclusion(expert_cot["grade_result"])
    )


def _image_data_url(image_path):
    path = Path(image_path)
    mime_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _recover_truncated_judge_response(text):
    first_error_match = re.search(
        r'"first_error_type"\s*:\s*"(none|visual|logical)"',
        text,
        flags=re.IGNORECASE,
    )
    if not first_error_match:
        return None

    def recover_string(field):
        match = re.search(
            rf'"{field}"\s*:\s*("(?:\\.|[^"\\])*")',
            text,
            flags=re.DOTALL,
        )
        if not match:
            return ""
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return ""

    return {
        "first_error_type": first_error_match.group(1).lower(),
        "error_step": recover_string("error_step"),
        "reason": recover_string("reason"),
    }


def _parse_judge_response(text):
    result = extract_json_object(text)
    if result is None:
        result = _recover_truncated_judge_response(text)
    if result is None:
        raise ValueError(f"Judge did not return recoverable JSON: {text}")

    required = {"first_error_type", "error_step", "reason"}
    if not required.issubset(result):
        raise ValueError(f"Judge response is missing fields: {required - set(result)}")

    first_error_type = str(result["first_error_type"]).strip().lower()
    if first_error_type not in {"none", "visual", "logical"}:
        raise ValueError("first_error_type must be none, visual, or logical")

    visual_correct = int(first_error_type != "visual")
    logical_correct = int(first_error_type == "none")

    return {
        "V": visual_correct,
        "L": logical_correct,
        "V_H": int(first_error_type == "visual"),
        "L_H": int(first_error_type == "logical"),
        "first_error_type": first_error_type,
        "error_step": str(result.get("error_step", "")).strip(),
        "judge_reason": str(result.get("reason", "")).strip(),
        "judge_response": text,
    }


def evaluate_cot_with_api(model_cot, expert_cot, image_path, client, judge_settings):
    system_prompt = """You are an expert in evaluating CoT reasoning for power transmission equipment defect grading. Review the visual descriptions and logical reasoning step by step in the order of the model's CoT, and identify the first error.

Follow these rules:

1. At each step, first check the visual description corresponding to that step. Compare only the information relevant to the current judgment. The model response does not need to use the same wording as the expert annotation. If the core meaning is approximately the same, treat the visual description as correct.

2. If the model's visual description clearly conflicts with the target image or expert annotation, lacks visual evidence, or omits a key visual fact that affects the current judgment, classify the first error as visual and stop immediately. Do not examine any subsequent visual descriptions or logical reasoning.

3. Only when the current visual description is correct should you examine the logical judgment based on that visual fact, including the decision-tree branch, reasoning transition, and grade mapping.

4. If the current logical judgment is incorrect, classify the first error as logical and stop immediately. Do not examine the remaining CoT.

5. If no error is found in any visual description or logical judgment throughout the CoT, classify the result as none.

6. Identify only the first error. Do not attribute downstream errors caused by an earlier error."""

    evaluation_prompt = f"""Evaluate the following model-generated CoT according to the rules above.

Expert-annotated CoT:
{json.dumps(expert_cot, ensure_ascii=False, indent=2)}

Model-generated CoT:
{model_cot}

Review the CoT in sequence and stop as soon as the first error is found. Output only the following JSON:

{{
  "first_error_type": "visual, logical, or none",
  "error_step": "the field or step containing the first error; use none when the CoT is fully correct",
  "reason": "briefly explain why the model description conflicts with the visual evidence or why the logical judgment is incorrect; use consistent when the CoT is fully correct"
}}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": evaluation_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": _image_data_url(image_path)},
                },
            ],
        },
    ]

    max_retries = judge_settings["max_retries"]
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=judge_settings["model"],
                messages=messages,
                stream=False,
                temperature=judge_settings["temperature"],
            )
            return _parse_judge_response(response.choices[0].message.content)
        except Exception:
            if attempt == max_retries:
                raise
            time.sleep(judge_settings["retry_delay_seconds"])


def evaluate_cot_sample(model_cot, expert_cot, image_path, client, judge_settings):
    evaluation = {
        "J": json_validity(model_cot, expert_cot),
        "B": branch_decision_correctness(model_cot, expert_cot),
        "F": final_grade_correctness(model_cot, expert_cot),
    }
    evaluation.update(
        evaluate_cot_with_api(
            model_cot,
            expert_cot,
            image_path,
            client,
            judge_settings,
        )
    )
    evaluation["fully_correct"] = (
        evaluation["J"]
        * evaluation["B"]
        * evaluation["F"]
        * evaluation["L"]
        * evaluation["V"]
    )
    return evaluation


def cot_reliability_metrics(evaluations):
    if not evaluations:
        raise ValueError("No CoT evaluations were provided")
    sample_count = len(evaluations)
    return {
        "ACC_FC_MCoT": sum(item["fully_correct"] for item in evaluations) / sample_count,
        "VHR_CoT": sum(item["V_H"] for item in evaluations) / sample_count,
        "LHR_CoT": sum(item["L_H"] for item in evaluations) / sample_count,
    }
