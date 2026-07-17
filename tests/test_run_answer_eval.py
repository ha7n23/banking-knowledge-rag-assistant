import pytest

from banking_rag.runners.run_answer_eval import (
    calculate_pass_rate,
    validate_min_pass_rate,
)


def test_calculate_pass_rate() -> None:
    assert calculate_pass_rate(passed=4, total=4) == 1.0
    assert calculate_pass_rate(passed=3, total=4) == 0.75


def test_calculate_pass_rate_handles_zero_total() -> None:
    assert calculate_pass_rate(passed=0, total=0) == 0.0


def test_validate_min_pass_rate_accepts_valid_values() -> None:
    validate_min_pass_rate(0.0)
    validate_min_pass_rate(0.5)
    validate_min_pass_rate(1.0)


def test_validate_min_pass_rate_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        validate_min_pass_rate(-0.1)

    with pytest.raises(ValueError):
        validate_min_pass_rate(1.1)