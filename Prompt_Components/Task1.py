"""Prompt components for Task1: tension-clamp crimping assessment."""

P_R = """【Role】 You are an expert in power transmission equipment defect grading. Your responsibility is to reliably grade defects based on the visible evidence in the image, the provided expert knowledge, and the grading decision tree.

The defect grades, ordered from most to least severe, are "Urgent", "Major", "Kind", and "Else". Not every task includes all four grades; always follow the grading decision tree specified for the current task."""

P_T = """【Task】 You need to determine the defect grade of Tension Clamp - Crimping. This task includes the "Else" and "Kind" grades.

In provided picture, please note the following:
1. In the image to be graded, the tension clamp is located within the blue box. First identify the position of the aluminum tube on the tension clamp.
2. One end of the aluminum tube is connected to the steel anchor, and the other end is connected to the conductor. If the connection structures are visible, determine whether the left and right ends are connected to the steel anchor or the conductor. Do not infer a connection that is not visible.
3. Crimping permanently deforms the aluminum tube using hydraulic or mechanical pressure, thereby forming a secure connection with the conductor. A crimped section generally has continuous hexagonal edges or a regularly flattened profile.
4. An angular or regularly flattened section indicates crimping, whereas a smooth cylindrical section indicates no crimping. Exclude false crimping features caused by illumination, highlights, shadows, corrosion, or image blur."""

P_DT = """【Decision Tree】 Proceed to inspect by sequentially executing the following decision-tree steps:

1. left_end_crimp: Is the left end of the aluminum tube a smooth cylindrical area?
   ├─ No → Crimping marks are present at the left end; the grade result is "Else".
   └─ Yes → Proceed to inspect the right end.

2. right_end_crimp: Is the right end of the aluminum tube a smooth cylindrical area?
   ├─ No → Crimping marks are present at the right end; the grade result is "Else".
   └─ Yes → Neither end has crimping marks; the grade result is "Kind"."""

P_F = """【Format】 Output must be valid JSON, with no fields added, removed, or renamed. Each value must follow the format "Conclusion | Reason". Output only the JSON object.

{
  "location_description": "Location of the blue box and the tension-clamp aluminum tube, including whether the left and right ends are connected to the steel anchor or the conductor",
  "left_end_crimp": "<Yes|No> | <Reason based on the shape of the left end of the aluminum tube>",
  "right_end_crimp": "<Yes|No> | <Reason based on the shape of the right end of the aluminum tube>",
  "grade_result": "<Else|Kind> | <Complete reason integrating the preceding observations according to the decision tree>"
}"""

P_RI = """【Reference Images】 Here are grading processes for crimp defects in four manually verified reference images. Please study and reference the thinking method and output format."""

P_RI_RESULT_ONLY = """【Reference Images】 Here are four manually verified reference images and their defect grades."""

P_OI = """【Objective Image】 This is the objective image:"""
P_OI_INSTRUCTION = """Please output the grading JSON."""

P_Q1_1 = """【Question1】 According to the given context, judge the defect grade of the objective image. Output only the final grade in the format ***Else*** or ***Kind***."""

P_Q1_2 = """【Question1】 According to the given context and GDT-based CoT grading logic, judge the defect grade of the objective image and output the complete grading process in the specified JSON format."""

P_Q1_3 = """【Question1】 According to the given context and informative grading cases, judge the defect grade of the objective image. Output only the final grade in the format ***Else*** or ***Kind***."""

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
