# NovetraSys NPAD Calculator with Presets
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="NovetraSys NPAD Calculator", layout="wide")

st.title("🏥 NovetraSys NPAD Calculator")
st.caption("Real-time PPO vs NPAD economics • Now with preset scenarios (Hospital CFO, TPA, Stop-Loss, Vinny Win)")

# ---------------- Presets -----------------
PRESETS = {
    "Custom (no preset)": {},
    "Hospital CFO (Inpatient focus)": {
        "actuarial_value": 0.842, "plan_writeoff": 0.02, "plan_dso_days": 55, "patient_dso_days": 45, "discount_rate": 0.08,
        "repay_small": 0.50, "repay_medium": 0.43, "repay_large": 0.34,
        "place_frac": 0.40, "recovery_rate": 0.15, "collector_fee": 0.25, "cash_day_collections": 150,
        "bir_op": 61.0, "bir_ip": 215.0,
        "allowed_small": 1000.0, "allowed_large": 10000.0
    },
    "TPA (Admin savings emphasis)": {
        "actuarial_value": 0.842, "plan_writeoff": 0.015, "plan_dso_days": 45, "patient_dso_days": 50, "discount_rate": 0.08,
        "repay_small": 0.52, "repay_medium": 0.45, "repay_large": 0.36,
        "place_frac": 0.35, "recovery_rate": 0.16, "collector_fee": 0.23, "cash_day_collections": 150,
        "bir_op": 50.0, "bir_ip": 190.0,
        "allowed_small": 1200.0, "allowed_large": 8000.0
    },
    "Stop-Loss (Risk guardrails)": {
        "actuarial_value": 0.86, "plan_writeoff": 0.02, "plan_dso_days": 50, "patient_dso_days": 60, "discount_rate": 0.08,
        "repay_small": 0.48, "repay_medium": 0.42, "repay_large": 0.32,
        "place_frac": 0.55, "recovery_rate": 0.14, "collector_fee": 0.27, "cash_day_collections": 180,
        "bir_op": 65.0, "bir_ip": 230.0,
        "allowed_small": 1500.0, "allowed_large": 20000.0
    },
    "Vinny Win (All 3 win)": {
        "actuarial_value": 0.842, "plan_writeoff": 0.015, "plan_dso_days": 40, "patient_dso_days": 15, "discount_rate": 0.08,
        "repay_small": 0.60, "repay_medium": 0.50, "repay_large": 0.45,
        "place_frac": 0.20, "recovery_rate": 0.18, "collector_fee": 0.20, "cash_day_collections": 90,
        "bir_op": 45.0, "bir_ip": 170.0,
        "allowed_small": 1000.0, "allowed_large": 10000.0
    }
}

# Initialize session state for all keys we'll use
DEFAULTS = {
    "actuarial_value": 0.842, "plan_writeoff": 0.02, "plan_dso_days": 55, "patient_dso_days": 60, "discount_rate": 0.08,
    "repay_small": 0.50, "repay_medium": 0.43, "repay_large": 0.34,
    "place_frac": 0.50, "recovery_rate": 0.15, "collector_fee": 0.25, "cash_day_collections": 180,
    "bir_op": 61.0, "bir_ip": 215.0,
    "allowed_small": 1000.0, "allowed_large": 10000.0
}
for k,v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

# Preset loader UI
colp1, colp2 = st.columns([2,1])
with colp1:
    preset_name = st.selectbox("🔧 Choose a preset", list(PRESETS.keys()), index=0)
with colp2:
    if st.button("Load preset"):
        preset = PRESETS.get(preset_name, {})
        for k,v in DEFAULTS.items():
            st.session_state[k] = preset.get(k, v)
        st.success(f"Loaded preset: {preset_name}")

# Sidebar controls bound to session_state
st.sidebar.header("Input Parameters")
st.session_state.actuarial_value = st.sidebar.slider("Plan Share (Actuarial Value)", 0.6, 0.95, st.session_state.actuarial_value, key="actuarial_value_slider")
st.session_state.plan_writeoff = st.sidebar.slider("Plan Write-off (%)", 0.0, 0.10, st.session_state.plan_writeoff, key="plan_writeoff_slider")
st.session_state.plan_dso_days = st.sidebar.slider("Plan Days to Collect", 0, 180, int(st.session_state.plan_dso_days), key="plan_dso_days_slider")
st.session_state.patient_dso_days = st.sidebar.slider("Patient Days to Collect", 0, 365, int(st.session_state.patient_dso_days), key="patient_dso_days_slider")
st.session_state.discount_rate = st.sidebar.slider("Discount Rate (annual)", 0.0, 0.25, float(st.session_state.discount_rate), key="discount_rate_slider")

st.sidebar.markdown("---")
st.sidebar.header("Patient Repayment Thresholds (fixed bands)")
st.session_state.repay_small = st.sidebar.number_input("Repayment ≤ $250", 0.0, 1.0, float(st.session_state.repay_small), key="repay_small_input")
st.session_state.repay_medium = st.sidebar.number_input("Repayment $250–$1,000", 0.0, 1.0, float(st.session_state.repay_medium), key="repay_medium_input")
st.session_state.repay_large = st.sidebar.number_input("Repayment > $1,000", 0.0, 1.0, float(st.session_state.repay_large), key="repay_large_input")
THRESH_SMALL = 250.0
THRESH_MED = 1000.0

st.sidebar.markdown("---")
st.sidebar.header("Collections Assumptions")
st.session_state.place_frac = st.sidebar.slider("% of Unpaid Sent to Collections", 0.0, 1.0, float(st.session_state.place_frac), key="place_frac_slider")
st.session_state.recovery_rate = st.sidebar.slider("Collections Recovery Rate", 0.0, 1.0, float(st.session_state.recovery_rate), key="recovery_rate_slider")
st.session_state.collector_fee = st.sidebar.slider("Collections Fee (% of recovered)", 0.0, 1.0, float(st.session_state.collector_fee), key="collector_fee_slider")
st.session_state.cash_day_collections = st.sidebar.slider("Collections Cash Day", 0, 720, int(st.session_state.cash_day_collections), key="cash_day_collections_slider")

st.sidebar.markdown("---")
st.sidebar.header("Billing & Insurance (BIR) Cost per Encounter")
st.session_state.bir_op = st.sidebar.number_input("Outpatient / ED", 0.0, 1000.0, float(st.session_state.bir_op), key="bir_op_input")
st.session_state.bir_ip = st.sidebar.number_input("Inpatient / Surgery", 0.0, 2000.0, float(st.session_state.bir_ip), key="bir_ip_input")

# Helper functions
def pv(amount, days, rate):
    return amount / ((1 + rate) ** (days / 365)) if amount != 0 else 0.0

def repay_rate(patient_owed):
    if patient_owed <= THRESH_SMALL:
        return st.session_state.repay_small
    elif patient_owed <= THRESH_MED:
        return st.session_state.repay_medium
    else:
        return st.session_state.repay_large

def calc_case(allowed, bir):
    plan_allowed = st.session_state.actuarial_value * allowed
    pat_allowed  = (1 - st.session_state.actuarial_value) * allowed

    plan_net = (1 - st.session_state.plan_writeoff) * plan_allowed
    plan_pv  = pv(plan_net, st.session_state.plan_dso_days, st.session_state.discount_rate)

    repay    = repay_rate(pat_allowed)
    pat_paid = repay * pat_allowed
    pat_pv   = pv(pat_paid, st.session_state.patient_dso_days, st.session_state.discount_rate)

    unpaid   = pat_allowed - pat_paid
    placed   = st.session_state.place_frac * unpaid
    recovered= st.session_state.recovery_rate * placed
    net_to_provider = (1 - st.session_state.collector_fee) * recovered
    coll_pv  = pv(net_to_provider, st.session_state.cash_day_collections, st.session_state.discount_rate)

    net_pv   = plan_pv + pat_pv + coll_pv - bir
    pct      = (net_pv / allowed) * 100 if allowed>0 else np.nan

    return pd.Series({
        "Allowed": allowed,
        "Plan PV": plan_pv,
        "Patient PV": pat_pv,
        "Collections PV": coll_pv,
        "BIR Cost": -bir,
        "Net PV": net_pv,
        "Net % of Allowed": pct,
        "Repay rate used": repay
    })

# Inputs for allowed amounts (bound to session_state)
st.header("Allowed Amounts")
c1, c2 = st.columns(2)
with c1:
    st.session_state.allowed_small = st.number_input("Small Case Allowed ($)", 100.0, 100000.0, float(st.session_state.allowed_small), key="allowed_small_input")
with c2:
    st.session_state.allowed_large = st.number_input("Large Case Allowed ($)", 100.0, 1000000.0, float(st.session_state.allowed_large), key="allowed_large_input")

# Pick BIR by magnitude (heuristic)
bir_small = st.session_state.bir_op if st.session_state.allowed_small <= 2000 else st.session_state.bir_ip
bir_large = st.session_state.bir_ip if st.session_state.allowed_large >= 5000 else st.session_state.bir_op

# Run calcs
df = pd.DataFrame([
    calc_case(st.session_state.allowed_small, bir_small),
    calc_case(st.session_state.allowed_large, bir_large)
], index=["Small Case","Large Case"])

st.subheader("Results (Present Value)")
st.dataframe(df.round(2))

st.subheader("Net % of Allowed — Comparison")
fig, ax = plt.subplots(figsize=(6,3))
ax.bar(df.index, df["Net % of Allowed"], color=["#2E86C1","#117A65"])
ax.set_ylabel("Net % of Allowed")
ax.set_ylim(0, 100)
for i,v in enumerate(df["Net % of Allowed"]):
    if not np.isnan(v):
        ax.text(i, v+1, f"{v:.1f}%", ha="center", fontweight="bold")
st.pyplot(fig)

with st.expander("View assumptions used"):
    st.json({
        "actuarial_value": st.session_state.actuarial_value,
        "plan_writeoff": st.session_state.plan_writeoff,
        "plan_dso_days": st.session_state.plan_dso_days,
        "patient_dso_days": st.session_state.patient_dso_days,
        "discount_rate": st.session_state.discount_rate,
        "repay_small": st.session_state.repay_small,
        "repay_medium": st.session_state.repay_medium,
        "repay_large": st.session_state.repay_large,
        "collections": {
            "place_frac": st.session_state.place_frac,
            "recovery_rate": st.session_state.recovery_rate,
            "collector_fee": st.session_state.collector_fee,
            "cash_day_collections": st.session_state.cash_day_collections
        },
        "bir_op": st.session_state.bir_op,
        "bir_ip": st.session_state.bir_ip,
        "allowed_small": st.session_state.allowed_small,
        "allowed_large": st.session_state.allowed_large
    })

st.markdown("""
**Notes**
- Default plan share = 0.842 (ESI in-network AV).
- Repayment by balance: ≤$250 ~50%; $250–$1,000 ~43%; >$1,000 ~34% (editable).
- Collections defaults: 50% of unpaid placed @120–180 days; 15% recovered; 25% fee.
- BIR per encounter defaults: $61 OP; $215 IP.
- Change any assumption and results update instantly.
""")

