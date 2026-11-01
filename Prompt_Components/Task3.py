"""Prompt components for Task3: tangent-tower bird-nest assessment."""

P_R = """【Role】 You are an expert in power transmission equipment defect grading. Your responsibility is to reliably grade defects based on the visible evidence in the image, the provided expert knowledge, and the grading decision tree.

The defect grades, ordered from most to least severe, are "Urgent", "Major", "Kind", and "Else". Not every task includes all four grades; always follow the grading decision tree specified for the current task."""

P_T = """【Task】 You need to determine the defect grade of Tangent Tower - Bird Nest. This task includes the "Else", "Kind", "Major", and "Urgent" grades.

In provided picture, please note the following:
1. In the image to be graded, the bird nest to be inspected is located within the blue box. First identify the position of the bird nest in the image.
2. A tangent tower consists of a vertical main body and outward-extending crossarms. Determine whether the bird nest is located on a crossarm and clearly away from the main body of the vertical tangent tower or concrete pole.
3. The insulators may be glass, ceramic, or composite insulators and are generally connected to the crossarm through metal fittings.
4. Bird nests are generally made of branches and straw. If no material is drooping, determine whether the nest is loose or has a large volume. If material is drooping, determine whether it is long enough to clearly exceed the length of the metal hangers connecting the insulators and tangent tower and whether it has wrapped around the insulator."""

P_DT = """【Decision Tree】 Execute the checks in Steps 1–4. If a No or Not is returned, the grading outcome shall be determined directly, and the subsequent check items are exempted from further evaluation.

1. Having insulator: Does the image contain at least one insulator string?
   ├─ Not Exists → The grade result is "Else".
   └─ Exists → Proceed to Step 2.

2. Nest location: Is the bird nest located on the crossarm, away from the main body of the vertical tangent tower or concrete pole?
   ├─ No → The grade result is "Else".
   └─ Yes → Proceed to Step 3.

3. Drooping: Do the straw, branches, or other materials hang down?
   ├─ No → Proceed to Step 4A.
   └─ Yes → Proceed to Step 4B.

4A. Nest Structure: Is the bird nest loose or of large volume?
   ├─ No → The grade result is "Kind".
   └─ Yes → The grade result is "Major".

4B. Drooping Length: Are the drooping materials long enough to clearly exceed the length of the metal hangers connecting the insulators and tangent tower, and have they wrapped around the insulator?
   ├─ No → The grade result is "Major".
   └─ Yes → The grade result is "Urgent"."""

P_F = """【Format】 Output must be valid JSON, with no fields added, removed, or renamed. Each value must follow the format "Conclusion | Reason". Output only the JSON object.

{
  "has_nest": "Location of the blue box and the bird nest in the image",
  "has_insulator": "<Yes|No> | <Reason>",
  "nest_type": "<Yes|No> | <Reason>",
  "material_droop": "<Yes|No> | <Reason>",
  "nest_stable": "<Yes|No> | <Reason>",
  "material_touch": "<Yes|No> | <Reason stating whether the drooping materials clearly exceed the metal-hanger length and have wrapped around the insulator>",
  "grade_result": "<Else|Kind|Major|Urgent> | <Complete reason integrating the preceding observations according to the decision tree>"
}"""

P_RI = """【Reference Images】 Here are grading processes for bird-nest defects in four manually verified reference images. Please study and reference the thinking method and output format."""

P_RI_RESULT_ONLY = """【Reference Images】 Here are four manually verified reference images and their defect grades."""

P_OI = """【Objective Image】 This is the objective image:"""
P_OI_INSTRUCTION = """Please output the grading JSON."""

P_Q1_1 = """【Question1】 According to the given context, judge the defect grade of the objective image. Output only the final grade in the format ***Else***, ***Kind***, ***Major***, or ***Urgent***."""

P_Q1_2 = """【Question1】 According to the given context and GDT-based CoT grading logic, judge the defect grade of the objective image and output the complete grading process in the specified JSON format."""

P_Q1_3 = """【Question1】 According to the given context and informative grading cases, judge the defect grade of the objective image. Output only the final grade in the format ***Else***, ***Kind***, ***Major***, or ***Urgent***."""

P_Q1_4 = """【Question1】 According to the given context and informative grading cases, judge the defect grade of the objective image."""

P_GR = """【Ground Truth】 The manually annotated ground-truth defect grade of the objective image is ***{ground_truth}***."""

P_Q2 = """【Question2】 According to the given context, objective image, and its matched ground-truth defect grade, elaborate the chain-of-thought (CoT) reasoning process for this image following the above CoT grading logic and JSON format demonstrated in the informative grading cases."""

COMPONENTS = {
    "role": P_R,
    "task": P_T,
    "decision_tree": P_DT,
    "format": P_F,
    "reference": P_RI,
    "reference_result_only": P_RI_RESULT_ONLY,
    "objective": P_OI,
    "objective_instruction": P_OI_INSTRUCTION,
    "question_1": P_Q1_1,
    "question_2": P_Q1_2,
    "question_3": P_Q1_3,
    "question_4": P_Q1_4,
    "ground_truth": P_GR,
    "annotation_question": P_Q2,
}
