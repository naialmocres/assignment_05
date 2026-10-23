"""
summarize.py — Step 2 of the pipeline: the roster on, then one row per employee.

Two halves:

1. **Finish the history** — put a readable name and a department on every row
   (one more `.str` function and a merge you have written before), and chain
   Steps 1 and 2 into `build_history`, the one call the app makes.
2. **Change the grain** — `summarize_employees` turns *one row per person per
   week* into *one row per person*. That is a **group by**: split the rows into
   groups that share a key, compute something for each group, combine the answers
   into a new table (lesson 3-5).

A group-by does not break the lineage rule; it starts a *new* table at a new
grain, and every number in it is traceable to a group of rows in the history.
What it must not do is change the history it was handed.

Less scaffolding here: the steps are described, the code is yours.
"""

import pandas as pd

from .history import add_clean_columns, add_date_parts, combine_exports


def format_name(names: pd.Series) -> pd.Series:
    """Turn HR's "Last, First" into "First Last" for a whole Series."""
    parts = names.str.split(",")
    first = parts.str[1].str.strip()
    last = parts.str[0].str.strip()
    return first + " " + last


def add_roster(history: pd.DataFrame, employees: pd.DataFrame) -> pd.DataFrame:
    """Return the history with display_name and department added from the roster."""
    roster = employees.copy()
    roster["display_name"] = format_name(roster["name"])
    roster = roster[["employee_id", "display_name", "department"]]
    return pd.merge(history, roster, on="employee_id", how="left")


def build_history(exports: list, employees: pd.DataFrame) -> pd.DataFrame:
    """Raw exports and roster in; the finished quarter history out."""
    history = combine_exports(exports)
    history = add_clean_columns(history)
    history = add_date_parts(history)
    return add_roster(history, employees)


def summarize_employees(history: pd.DataFrame) -> pd.DataFrame:
    """One row per employee, summarizing weeks, hours, and pay."""
    summary = (
        history.groupby(["employee_id", "display_name", "department"])
        .agg(
            weeks_paid=("week_ending", "count"),
            total_hours=("hours_worked", "sum"),
            total_pay=("gross_pay", lambda s: round(s.sum(), 2)),
            avg_hours=("hours_worked", lambda s: round(s.mean(), 2)),
            overtime_weeks=("hours_worked", lambda s: (s > 40.0).sum()),
        )
        .reset_index()
    )
    summary = summary[
        [
            "employee_id",
            "display_name",
            "department",
            "weeks_paid",
            "total_hours",
            "total_pay",
            "avg_hours",
            "overtime_weeks",
        ]
    ]
    return summary.sort_values("employee_id").reset_index(drop=True)
