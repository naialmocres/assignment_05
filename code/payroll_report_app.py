"""Streamlit dashboard for the quarterly payroll report."""

import pandas as pd
import streamlit as st

from payroll import (
    build_history,
    hours_grid,
    load_employees,
    load_export,
    missed_weeks,
    pay_by_month,
    summarize_employees,
)


st.title("Salt City Coffee — Quarterly Payroll Report")

roster = load_employees()
uploads = st.file_uploader("Uploads", type=["csv"], accept_multiple_files=True, key="exports")

if uploads:
    history = build_history([load_export(upload) for upload in uploads], roster)

    unmatched = (
        history.loc[history["department"].isna(), "employeeid"]
        .drop_duplicates()
        .tolist()
    )
    if unmatched:
        st.warning(f"Unmatched employee IDs were left out of the report: {', '.join(unmatched)}")

    clean_history = history[history["department"].notna()].copy()
    departments = ["All"] + sorted(clean_history["department"].dropna().unique().tolist())
    department = st.selectbox("Department", departments, key="department")

    first_date = clean_history["pay_date"].min().date()
    last_date = clean_history["pay_date"].max().date()
    dates = st.date_input(
        "Pay dates",
        value=(first_date, last_date),
        min_value=first_date,
        max_value=last_date,
        key="dates",
    )

    if isinstance(dates, tuple) and len(dates) == 2:
        start_date, end_date = dates
    else:
        start_date = end_date = dates

    selected = clean_history.copy()
    if department != "All":
        selected = selected[selected["department"] == department]
    selected = selected[
        (selected["pay_date"].dt.date >= start_date) & (selected["pay_date"].dt.date <= end_date)
    ].copy()

    st.subheader("Quarterly payroll overview")

    metrics = st.columns(4)
    with metrics[0]:
        st.metric("Weeks", selected["pay_date"].dt.date.nunique())
    with metrics[1]:
        st.metric("Employees", selected["employee_id"].nunique())
    with metrics[2]:
        st.metric("Total hours", f"{selected['hours_worked'].sum():,.2f}")
    with metrics[3]:
        st.metric("Total gross pay", f"${selected['gross_pay'].sum():,.2f}")

    monthly = pay_by_month(selected)
    st.bar_chart(monthly, x="month")

    st.dataframe(summarize_employees(selected), width="stretch")

    grid = hours_grid(selected)
    st.dataframe(grid, width="stretch")
    st.dataframe(missed_weeks(grid), width="stretch")

    csv_data = monthly.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="pay_by_month.csv",
        mime="text/csv",
        key="download",
    )
