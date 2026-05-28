from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_EXPECTATIONS_DIR = Path(__file__).resolve().parents[3] / "great_expectations" / "expectations"


@dataclass(frozen=True)
class ValidationResult:
    dataset: str
    success: bool
    failed_expectations: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "success": self.success,
            "failed_expectations": self.failed_expectations,
        }


def load_expectation_suite(dataset: str, expectations_dir: Path | None = None) -> dict[str, Any]:
    suite_path = (expectations_dir or DEFAULT_EXPECTATIONS_DIR) / f"{dataset}.json"
    with suite_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_dataframe(
    df: pd.DataFrame,
    dataset: str,
    expectations_dir: Path | None = None,
    fail_fast: bool = False,
) -> ValidationResult:
    """Validate a dataframe using a Great Expectations suite JSON.

    The project stores GE suites as the source of truth. This lightweight runner
    supports the expectation types used in the assignment and keeps DAG runtime
    deterministic in minimal Docker environments.
    """
    suite = load_expectation_suite(dataset, expectations_dir)
    failures: list[str] = []

    for expectation in suite["expectations"]:
        expectation_type = expectation["expectation_type"]
        kwargs = expectation.get("kwargs", {})
        label = f"{expectation_type}({kwargs})"

        if expectation_type == "expect_table_row_count_to_be_between":
            min_value = kwargs.get("min_value", 0)
            max_value = kwargs.get("max_value")
            ok = len(df) >= min_value and (max_value is None or len(df) <= max_value)
        elif expectation_type == "expect_column_values_to_not_be_null":
            ok = df[kwargs["column"]].notna().all()
        elif expectation_type == "expect_column_values_to_be_unique":
            ok = not df[kwargs["column"]].duplicated().any()
        elif expectation_type == "expect_column_values_to_be_between":
            series = df[kwargs["column"]]
            min_value = kwargs.get("min_value")
            max_value = kwargs.get("max_value")
            ok = (min_value is None or series.ge(min_value).all()) and (
                max_value is None or series.le(max_value).all()
            )
        elif expectation_type == "expect_column_values_to_be_in_set":
            ok = df[kwargs["column"]].isin(kwargs["value_set"]).all()
        else:
            raise NotImplementedError(f"Unsupported expectation type: {expectation_type}")

        if not ok:
            failures.append(label)
            if fail_fast:
                break

    return ValidationResult(dataset=dataset, success=not failures, failed_expectations=failures)


def assert_valid(df: pd.DataFrame, dataset: str, expectations_dir: Path | None = None) -> ValidationResult:
    result = validate_dataframe(df, dataset, expectations_dir)
    if not result.success:
        raise ValueError(f"Data quality failed for {dataset}: {result.failed_expectations}")
    return result

