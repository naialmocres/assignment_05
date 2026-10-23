"""
reshape.py — Step 3 of the pipeline: the same numbers, turned sideways.

A **long** table has one row per observation (person, week, hours). A **wide**
table spreads one of those columns across the top, so a whole row reads like a
line on a timecard. People read wide tables; pipelines store long ones; and
lesson 3-5's `pivot_table` and `melt` turn one into the other.

Three functions:

- `hours_grid` — long to wide: employees down the side, weeks across the top.
- `missed_weeks` — wide back to long, to find something the long table could
  never show you: the weeks a person was **not** paid. Nobody's absence is a row
  in an export. It only exists once the grid has filled the gap with a zero.
- `pay_by_month` — months down the side, departments across the top: the table
  the accountant asked for, and the shape `st.bar_chart` wants.

No walkthrough. The docstrings say what each function returns; `tests/` says
how that is checked. None of these functions may change the frame it is given.
"""

import pandas as pd


def hours_grid(history: pd.DataFrame) -> pd.DataFrame:
    """Employees down the side, weeks across the top, hours in the cells."""
    grid = (
        history.pivot_table(
            index=["employee_id", "display_name"],
            columns="week_ending",
            values="hours_worked",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .sort_values("employee_id")
        .reset_index(drop=True)
    )
    return grid


def missed_weeks(grid: pd.DataFrame) -> pd.DataFrame:
    """Every (employee, week) with zero hours in the grid — the weeks people missed."""
    melted = grid.melt(
        id_vars=["employee_id", "display_name"],
        var_name="week_ending",
        value_name="hours_worked",
    )
    return (
        melted[melted["hours_worked"] == 0]
        .sort_values(["employee_id", "week_ending"])
        .reset_index(drop=True)
    )


def pay_by_month(history: pd.DataFrame) -> pd.DataFrame:
    """Total gross pay by month (rows) and department (columns), to the cent."""
    monthly = (
        history.groupby(["month", "department"], as_index=False)["gross_pay"]
        .sum()
        .pivot(index="month", columns="department", values="gross_pay")
        .fillna(0.0)
        .sort_index(axis=0)
        .sort_index(axis=1)
        .reset_index()
    )
    monthly.columns.name = None
    return monthly[["month"] + sorted(monthly.columns[1:])]
