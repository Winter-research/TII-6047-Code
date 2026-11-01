def _validate_grades(y_true, y_pred, labels):
    if not y_true:
        raise ValueError("No samples were provided")
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    if len(labels) < 2 or len(set(labels)) != len(labels):
        raise ValueError("labels must contain at least two unique grades")

    allowed = set(labels)
    invalid_true = sorted(set(y_true) - allowed)
    invalid_pred = sorted(set(y_pred) - allowed)
    if invalid_true or invalid_pred:
        raise ValueError(
            f"Unknown grades: true={invalid_true}, predicted={invalid_pred}"
        )


def confusion_matrix(y_true, y_pred, labels):
    _validate_grades(y_true, y_pred, labels)
    label_to_index = {label: index for index, label in enumerate(labels)}
    matrix = [[0 for _ in labels] for _ in labels]
    for true_grade, predicted_grade in zip(y_true, y_pred):
        matrix[label_to_index[true_grade]][label_to_index[predicted_grade]] += 1
    return matrix


def accuracy(y_true, y_pred):
    if not y_true or len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must be non-empty and equally sized")
    return sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true)


def per_class_precision_recall_f1(y_true, y_pred, labels):
    matrix = confusion_matrix(y_true, y_pred, labels)
    values = {}

    for index, label in enumerate(labels):
        true_positive = matrix[index][index]
        false_positive = sum(matrix[row][index] for row in range(len(labels))) - true_positive
        false_negative = sum(matrix[index]) - true_positive
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        values[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    return values


def macro_precision(y_true, y_pred, labels):
    values = per_class_precision_recall_f1(y_true, y_pred, labels)
    return sum(item["precision"] for item in values.values()) / len(labels)


def macro_recall(y_true, y_pred, labels):
    values = per_class_precision_recall_f1(y_true, y_pred, labels)
    return sum(item["recall"] for item in values.values()) / len(labels)


def macro_f1(y_true, y_pred, labels):
    values = per_class_precision_recall_f1(y_true, y_pred, labels)
    return sum(item["f1"] for item in values.values()) / len(labels)


def normalized_macro_mae(y_true, y_pred, labels):
    matrix = confusion_matrix(y_true, y_pred, labels)
    grade_count = len(labels)
    total = 0.0

    for true_index, row in enumerate(matrix):
        class_count = sum(row)
        if class_count == 0:
            raise ValueError(f"No ground-truth samples found for grade: {labels[true_index]}")
        class_error = sum(
            count * abs(true_index - predicted_index)
            for predicted_index, count in enumerate(row)
        )
        total += class_error / class_count

    return total / (grade_count * (grade_count - 1))


def highest_severity_recall(y_true, y_pred, labels):
    values = per_class_precision_recall_f1(y_true, y_pred, labels)
    return values[labels[-1]]["recall"]


def over_grading_rate(y_true, y_pred, labels):
    _validate_grades(y_true, y_pred, labels)
    order = {label: index for index, label in enumerate(labels)}
    return sum(order[predicted] > order[true] for true, predicted in zip(y_true, y_pred)) / len(y_true)


def under_grading_rate(y_true, y_pred, labels):
    _validate_grades(y_true, y_pred, labels)
    order = {label: index for index, label in enumerate(labels)}
    return sum(order[predicted] < order[true] for true, predicted in zip(y_true, y_pred)) / len(y_true)


def grading_metrics(y_true, y_pred, labels):
    return {
        "ACC": accuracy(y_true, y_pred),
        "MP": macro_precision(y_true, y_pred, labels),
        "MR": macro_recall(y_true, y_pred, labels),
        "MF1": macro_f1(y_true, y_pred, labels),
        "NMAE": normalized_macro_mae(y_true, y_pred, labels),
        "R_K": highest_severity_recall(y_true, y_pred, labels),
        "over_grading_rate": over_grading_rate(y_true, y_pred, labels),
        "under_grading_rate": under_grading_rate(y_true, y_pred, labels),
    }
