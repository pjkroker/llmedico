from dataclasses import dataclass


@dataclass
class EvaluationMetricRow:
    class_fqn: str
    param_precision: float
    param_recall: float
    return_precision: float
    return_recall: float
    throws_precision: float
    throws_recall: float
    overall_precision: float
    overall_recall: float
    overall_f1: float = None
