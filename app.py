# ===== FILE: app.py =====

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

from models import Household, PersonProfile, AccountBalances, IncomeBreakdown
from simulator import simulate
from reporting import summarize, to_rows
from reporting_mtr import marginal_tax_curve
from scenarios import Scenario, run_scenarios, tweak_retire_age, tweak_cpp_oas
from mc import run_mc


def build_demo_household():
    return Household(
        person1=PersonProfile(
            name="You", age=60, province="AB", retirement_age=65,
            balances=AccountBalances(rrsp=800000, tfsa=150000, non_reg_mv=250000, non_reg_acb=200000),
            employment_income=120000, savings_rate=0.15
        ),
        person2=PersonProfile(
            name="Spouse", age=58, province="AB", retirement_age=65,
            balances=AccountBalances(rrsp=350000, tfsa=80000, non_reg_mv=50000, non_reg_acb=45000),
            employment_income=80000, savings_rate=0.12
        ),
        annual_expenses=80000
    )


def fig_to_png_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    return buf.getvalue()


st.set_page_config(page_title="Investors-Edge Planner", layout="wide")
st.title("Investors-Edge Retirement Planner")

tab_overview, tab_scenarios, tab_mtr = st.tabs(["📊 Overview", "📈 Scenarios", "📐 Marginal Tax Rates"])

with tab_overview:
    st.header("Overview")
    years = st.slider("Projection years", 5, 50, 35)
    start_year = st.number_input("Start year", value=2024)
    hh = build_demo_household()

    # Monte Carlo toggle
    run_mc_toggle = st.checkbox("Run Monte Carlo simulation")
    mc_runs = st.number_input("MC runs", min_value=100, max_value=5000, value=500, step=100) if run_mc_toggle else None

    results = simulate(hh, years=years, start_year=start_year)
    path = results if isinstance(results, list) else results[0]

    # Summary stats
    summary = summarize(path)
    st.subheader("Summary")
    st.json(summary)

    # If MC enabled, run and display stats
    if run_mc_toggle:
        mc_stats = run_mc(lambda hh_, **kw: simulate(hh_, years=years, start_year=start_year),
                          mc_runs, hh)
        st.subheader("Monte Carlo results")
        st.write(f"Probability of depletion: {mc_stats['prob_depletion']:.1%}")
        st.write(f"Median estate: ${mc_stats['estate_p50']:,.0f}")
        st.write(f"10th percentile estate: ${mc_stats['estate_p10']:,.0f}")
        st.write(f"90th percentile estate: ${mc_stats['estate_p90']:,.0f}")

    # Balances chart
    st.subheader("Account balances")
    fig_bal, ax_bal = plt.subplots()
    years_idx = [r.year_index for r in path]
    p1_rrsp = [r.balances_p1.rrsp for r in path]
    p1_tfsa = [r.balances_p1.tfsa for r in path]
    p1_nonreg = [r.balances_p1.non_reg_mv for r in path]
    ax_bal.stackplot(years_idx, p1_rrsp, p1_tfsa, p1_nonreg, labels=["RRSP", "TFSA", "Non-reg"])
    if path[0].balances_p2:
        p2_rrsp = [r.balances_p2.rrsp for r in path]
        p2_tfsa = [r.balances_p2.tfsa for r in path]
        p2_nonreg = [r.balances_p2.non_reg_mv for r in path]
        ax_bal.stackplot(years_idx, p2_rrsp, p2_tfsa, p2_nonreg,
                         labels=["P2 RRSP", "P2 TFSA", "P2 Non-reg"], alpha=0.5)
    ax_bal.legend(loc="upper left")
    st.pyplot(fig_bal)

    # Cash flow chart
    st.subheader("Net cash flow")
    fig_cf, ax_cf = plt.subplots()
    ax_cf.plot(years_idx, [r.net_cash_flow for r in path], marker="o")
    ax_cf.axhline(0, color="gray", linewidth=1)
    st.pyplot(fig_cf)

    # Export buttons
    df = pd.DataFrame(to_rows(path))
    csv_bytes = df.to_csv(index=False).encode()
    st.download_button("📥 Download data as CSV", data=csv_bytes, file_name="projection.csv", mime="text/csv")

    bal_png = fig_to_png_bytes(fig_bal)
    cf_png = fig_to_png_bytes(fig_cf)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📥 Download balances chart (PNG)", data=bal_png, file_name="balances.png", mime="image/png")
    with c2:
        st.download_button("📥 Download cash flow chart (PNG)", data=cf_png, file_name="cashflow.png", mime="image/png")

    st.subheader("Year-by-year data")
    st.dataframe(df)

with tab_scenarios:
    st.header("Scenario Comparison")
    years = st.slider("Projection years (scenarios)", 5, 50, 35, key="scen_years")
    start_year = st.number_input("Start year (scenarios)", value=2024, key="scen_start")
    base = build_demo_household()

    scenarios = [
        Scenario(name="Retire@65_CPP/OAS@65", tweak=tweak_retire_age(65), sim_years=years),
        Scenario(name="Retire@60_CPP/OAS@65", tweak=tweak_retire_age(60), sim_years=years),
        Scenario(name="Retire@65_CPP@70_OAS@70", tweak=lambda h: tweak_cpp_oas(70, 70)(tweak_retire_age(65)(h)), sim_years=years),
    ]
    runs = run_scenarios(base, scenarios, start_year=start_year)

    comp_rows = []
    for name, path in runs.items():
        results = path if isinstance(path, list) else path[0]
        summary = summarize(results)
        comp_rows.append({"Scenario": name, **summary})
    df_comp = pd.DataFrame(comp_rows)
    st.dataframe(df_comp, use_container_width=True)

    # Pick a scenario to chart
    choice = st.selectbox("Select scenario to view net cash flow", df_comp["Scenario"])
    sel_path = runs[choice] if isinstance(runs[choice], list) else runs[choice][0]
    fig_cf2, ax_cf2 = plt.subplots()
    years_idx = [r.year_index for r in sel_path]
    ax_cf2.plot(years_idx, [r.net_cash_flow for r in sel_path], marker="o")
    ax_cf2.axhline(0, color="gray", linewidth=1)
    ax_cf2.set_title(f"Net cash flow: {choice}")
    st.pyplot(fig_cf2)

with tab_mtr:
    st.header("Marginal Tax Rate Curve")
    province = st.selectbox("Province", ["AB", "BC", "ON", "QC"])
    age = st.number_input("Age", value=68)
    year = st.number_input("Tax year", value=2024)
    base_inc = IncomeBreakdown(
        rrif=st.number_input("RRIF income", value=40000.0),
        cpp=st.number_input("CPP income", value=14000.0),
        oas=st.number_input("OAS income", value=9000.0),
        interest=st.number_input("Interest income", value=2000.0),
        eligible_dividends=st.number_input("Eligible dividends", value=3000.0)
    )
    bumps = st.multiselect("Income bumps to test", [1000, 2000, 5000, 10000], default=[1000, 5000, 10000])
    if st.button("Generate MTR curve"):
        curve = marginal_tax_curve(province=province, age=age, year=year, base_inc=base_inc, bumps=bumps)
        df_curve = pd.DataFrame(curve)
        st.dataframe(df_curve, use_container_width=True)
        fig_mtr, ax_mtr = plt.subplots()
        ax_mtr.plot(df_curve["bump"], df_curve["marginal_rate"] * 100, marker="o")
        ax_mtr.set_ylabel("MTR (%)")
        ax_mtr.set_xlabel("Income bump ($)")
        st.pyplot(fig_mtr)
