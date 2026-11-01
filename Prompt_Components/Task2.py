"""Prompt components for Task2: guying-fitting corrosion assessment."""

P_R = """【Role】 You are an expert in power transmission equipment defect grading. Your responsibility is to reliably grade defects based on the visible evidence in the image, the provided expert knowledge, and the grading decision tree.

The defect grades, ordered from most to least severe, are "Urgent", "Major", "Kind", and "Else". Not every task includes all four grades; always follow the grading decision tree specified for the current task."""

P_T = """【Task】 You need to determine the defect grade of Guying Fitting - Corrosion. This task includes the "Else", "Kind", and "Major" grades.

In provided picture, please note the following:
1. In the image to be graded, the guying fitting to be inspected is located within the blue box. First identify its position and overall structure.
2. A guying fitting in normal condition is generally bright silver or bright yellow. After prolonged exposure to wind and rain, rust generally appears dark reddish-brown, dark gray, or black.
3. Minor corrosion generally covers only a local area, leaving the original metallic color clearly visible. Extensive corrosion covers more than half of the fitting surface and, in severe cases, approaches or exceeds three quarters, making the original color difficult to identify.
4. As corrosion progresses, the surface may become visibly granular, heavily burred, or uneven, and the structure may show visible weathering, damage, or deformation. Assess the corroded area, surface roughness, and structural integrity together."""

P_DT = """【Decision Tree】 Proceed to inspect by sequentially executing the following decision-tree steps:

1. degree_of_rusting: Does extensive corrosion clearly cover well over half of the fitting body?
   ├─ No → Proceed to Step 2A.
   └─ Yes → Proceed to Step 2B.

2A. smoothness_and_architecture: Does the fitting surface show pronounced burr-like roughness, or does the structure show weathering, damage, or deformation?
   ├─ No → The grade result is "Else".
   └─ Yes → The grade result is "Major".

2B. smoothness_and_architecture: Does the fitting surface show pronounced burr-like roughness or loss of smoothness, or does the structure show weathering, damage, or deformation?
   ├─ No → The grade result is "Kind".
   └─ Yes → The grade result is "Major"."""

P_F = """【Format】 Output must be valid JSON, with no fields added, removed, or renamed. Each value must follow the format "Conclusion | Reason". Output only the JSON object.

{
  "location_description": "Location of the blue box and the guying fitting in the image",
  "degree_of_rusting": "<Yes|No> | <Reason based on the corrosion color and coverage area>",
  "smoothness_and_architecture": "<Yes|No> | <Reason based on surface roughness and structural integrity>",
  "grade_result": "<Else|Kind|Major> | <Complete reason integrating the preceding observations according to the decision tree>"
}"""

P_RI = """【Reference Images】 Here are grading processes for corrosion defects in three manually verified reference images. Please study and reference the thinking method and output format."""

P_RI_RESULT_ONLY = """【Reference Images】 Here are three manually verified reference images and their defect grades."""

P_OI = """【Objective Image】 This is the objective image:"""
P_OI_INSTRUCTION = """Please output the grading JSON."""

P_Q1_1 = """【Question1】 According to the given context, judge the defect grade of the objective image. Output only the final grade in the format ***Else***, ***Kind***, or ***Major***."""

P_Q1_2 = """【Question1】 According to the given context and GDT-based CoT grading logic, judge the defect grade of the objective image and output the complete grading process in the specified JSON format."""

P_Q1_3 = """【Question1】 According to the given context and informative grading cases, judge the defect grade of the objective image. Output only the final grade in the format ***Else***, ***Kind***, or ***Major***."""

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
