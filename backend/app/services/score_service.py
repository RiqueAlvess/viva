"""
HSE-IT scoring logic.
7 dimensions:
- demandas (NEGATIVE): questions [3,6,9,12,16,18,20,22]
- controle (POSITIVE): questions [2,10,15,19,25,30]
- apoio_chefia (POSITIVE): questions [8,23,29,33,35]
- apoio_colegas (POSITIVE): questions [7,24,27,31]
- relacionamentos (NEGATIVE): questions [5,14,21,34]
- cargo (POSITIVE): questions [1,4,11,13,17]
- comunicacao_mudancas (POSITIVE): questions [26,28,32]
"""
from decimal import Decimal
from typing import Dict, Tuple

DIMENSIONS: Dict[str, Tuple[list[int], str]] = {
    "demandas": ([3, 6, 9, 12, 16, 18, 20, 22], "negative"),
    "controle": ([2, 10, 15, 19, 25, 30], "positive"),
    "apoio_chefia": ([8, 23, 29, 33, 35], "positive"),
    "apoio_colegas": ([7, 24, 27, 31], "positive"),
    "relacionamentos": ([5, 14, 21, 34], "negative"),
    "cargo": ([1, 4, 11, 13, 17], "positive"),
    "comunicacao_mudancas": ([26, 28, 32], "positive"),
}

SEVERITY_DEFAULT = Decimal("2")

RISK_PROBABILITY_MAP = {
    "aceitavel": Decimal("1"),
    "moderado": Decimal("2"),
    "importante": Decimal("3"),
    "critico": Decimal("4"),
}


def calculate_dimension_score(answers: dict, questions: list[int]) -> Decimal:
    """Calculate average score for a dimension."""
    values = []
    for q in questions:
        key = f"q{q}"
        if key in answers:
            val = answers[key]
            if isinstance(val, (int, float)) and 1 <= val <= 5:
                values.append(Decimal(str(val)))
    if not values:
        return Decimal("0")
    return sum(values) / Decimal(str(len(values)))


def get_risk_level(score: Decimal, direction: str) -> str:
    """Determine risk level based on score and dimension direction."""
    if direction == "negative":
        if score >= Decimal("4.0"):
            return "critico"
        elif score >= Decimal("3.0"):
            return "importante"
        elif score >= Decimal("2.0"):
            return "moderado"
        else:
            return "aceitavel"
    else:  # positive
        if score <= Decimal("2.0"):
            return "critico"
        elif score <= Decimal("3.0"):
            return "importante"
        elif score <= Decimal("4.0"):
            return "moderado"
        else:
            return "aceitavel"


def calculate_nr_value(risk_level: str, severity: Decimal = SEVERITY_DEFAULT) -> Decimal:
    """NR = Probability × Severity."""
    probability = RISK_PROBABILITY_MAP.get(risk_level, Decimal("1"))
    return probability * severity


def score_response(answers: dict) -> Dict[str, dict]:
    """
    Returns dict of {dimension: {score, risk_level, nr_value}} for all 7 dimensions.
    """
    results = {}
    for dimension, (questions, direction) in DIMENSIONS.items():
        score = calculate_dimension_score(answers, questions)
        risk_level = get_risk_level(score, direction)
        nr_value = calculate_nr_value(risk_level)
        results[dimension] = {
            "score": score,
            "risk_level": risk_level,
            "nr_value": nr_value,
            "direction": direction,
        }
    return results


def calculate_igrp(dimension_results_list: list[Dict[str, dict]]) -> Decimal:
    """
    IGRP = average of all NR values across all responses and dimensions.
    """
    all_nr_values = []
    for response_dims in dimension_results_list:
        for dim_data in response_dims.values():
            all_nr_values.append(dim_data["nr_value"])
    if not all_nr_values:
        return Decimal("0")
    return sum(all_nr_values) / Decimal(str(len(all_nr_values)))
