import sys
import math
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.predict import predict

st.set_page_config(page_title="Credit Scoring", page_icon="💳", layout="wide",
                   initial_sidebar_state="expanded")

# ----------------------------------------------------------------------------
# DESIGN SYSTEM (one set of tokens used by every component)
# ----------------------------------------------------------------------------
CSS = """
<style>
:root{
  --bg:#0e0e13; --surface:#16161d; --surface-2:#1d1d27; --border:rgba(255,255,255,.08);
  --text:#f4f4f7; --muted:#a3a3b2; --accent:#f58a1f; --accent-2:#c72c41;
  --good:#3ddc97; --warn:#ffc857; --bad:#ff6b6b;
  --radius:14px; --shadow:0 8px 28px rgba(0,0,0,.45);
}
.stApp{ background:radial-gradient(1100px 500px at 15% -10%, rgba(199,44,65,.18), transparent 60%), var(--bg); }
[data-testid="stHeader"]{ background:transparent; }
.block-container{ max-width:1100px; padding-top:2rem; padding-bottom:3rem; }
html, body, [class*="css"]{ font-family:"Segoe UI",Inter,system-ui,-apple-system,sans-serif; }

/* Typography hierarchy */
h1,h2,h3,p,label,span{ color:var(--text); }
.hero h1{ font-size:2.1rem; font-weight:750; letter-spacing:-.5px; margin:0 0 .25rem; }
.hero p{ color:var(--muted); font-size:1rem; margin:0; }
.badge{ display:inline-block; font-size:.72rem; font-weight:600; letter-spacing:.8px; text-transform:uppercase;
  color:var(--accent); border:1px solid rgba(245,138,31,.4); padding:.2rem .6rem; border-radius:99px; margin-bottom:.7rem; }
.section-title{ font-size:.8rem; font-weight:650; letter-spacing:1px; text-transform:uppercase; color:var(--muted); margin:.2rem 0 .6rem; }

/* Entrance animation */
@keyframes slideUp{ from{opacity:0; transform:translateY(14px);} to{opacity:1; transform:none;} }
.hero, [data-testid="stForm"], .result-wrap{ animation:slideUp .5s ease both; }

/* Form card */
[data-testid="stForm"]{ background:var(--surface); border:1px solid var(--border); border-radius:var(--radius);
  padding:1.6rem 1.6rem 1.2rem; box-shadow:var(--shadow); }
[data-testid="stWidgetLabel"] p{ color:var(--muted); font-size:.85rem; font-weight:550; }

/* Inputs */
div[data-baseweb="select"] > div, div[data-baseweb="input"]{
  background:var(--surface-2) !important; border:1px solid var(--border) !important; border-radius:10px !important;
  transition:border-color .2s, box-shadow .2s; }
div[data-baseweb="select"] > div:hover, div[data-baseweb="input"]:hover{ border-color:rgba(255,255,255,.22) !important; }
div[data-baseweb="select"] > div:focus-within, div[data-baseweb="input"]:focus-within{
  border-color:var(--accent) !important; box-shadow:0 0 0 3px rgba(245,138,31,.18); }
div[data-baseweb="input"] input, div[data-baseweb="select"] *{ color:var(--text) !important; background:transparent; }
div[data-baseweb="popover"] ul{ background:var(--surface-2) !important; }
div[data-baseweb="popover"] li:hover{ background:rgba(245,138,31,.15) !important; }
.stNumberInput button{ background:transparent !important; color:var(--muted) !important; }
[data-testid="stSlider"] [role="slider"]{ background:var(--accent) !important; box-shadow:0 0 0 4px rgba(245,138,31,.2); }
[data-testid="stExpander"]{ border:1px solid var(--border); border-radius:10px; background:transparent; }

/* Primary button */
.stButton > button, [data-testid="stFormSubmitButton"] > button{
  background:linear-gradient(135deg,var(--accent-2),var(--accent)); color:#fff !important; font-weight:700;
  border:none; border-radius:10px; padding:.7rem 1.5rem; width:100%;
  transition:transform .15s ease, box-shadow .15s ease, filter .15s ease; }
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover{
  transform:translateY(-2px); box-shadow:0 8px 22px rgba(245,138,31,.35); filter:brightness(1.06); }
.stButton > button:active, [data-testid="stFormSubmitButton"] > button:active{ transform:translateY(0); }
.stButton > button:focus-visible, [data-testid="stFormSubmitButton"] > button:focus-visible{ outline:3px solid #fff; outline-offset:2px; }

/* Cards */
.card{ background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:1.3rem 1.4rem;
  box-shadow:var(--shadow); transition:transform .2s ease, border-color .2s ease; height:100%; }
.card:hover{ transform:translateY(-3px); border-color:rgba(245,138,31,.35); }
.kpi-label{ color:var(--muted); font-size:.78rem; font-weight:600; letter-spacing:.6px; text-transform:uppercase; }
.kpi-value{ font-size:1.7rem; font-weight:750; margin-top:.25rem; }
.kpi-sub{ color:var(--muted); font-size:.82rem; margin-top:.15rem; }

/* Result */
.result-wrap{ margin-top:1.6rem; }
.gauge{ position:relative; width:170px; height:170px; margin:0 auto; }
.gauge svg{ transform:rotate(-90deg); }
.ring-bg{ stroke:rgba(255,255,255,.08); }
@keyframes drawRing{ from{ stroke-dashoffset:339.29; } }
.ring{ stroke-linecap:round; animation:drawRing 1.1s cubic-bezier(.2,.8,.2,1) both; }
.gauge-center{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }
.gauge-num{ font-size:2.2rem; font-weight:800; line-height:1; }
.gauge-cap{ color:var(--muted); font-size:.75rem; margin-top:.25rem; }
.status{ display:inline-flex; align-items:center; gap:.5rem; font-weight:700; padding:.35rem .9rem; border-radius:99px; font-size:.95rem; }
.status.good{ color:var(--good); background:rgba(61,220,151,.12); border:1px solid rgba(61,220,151,.35); }
.status.warn{ color:var(--warn); background:rgba(255,200,87,.12); border:1px solid rgba(255,200,87,.35); }
.status.bad { color:var(--bad);  background:rgba(255,107,107,.12); border:1px solid rgba(255,107,107,.35); }
.row{ display:flex; justify-content:space-between; padding:.55rem 0; border-bottom:1px solid var(--border); font-size:.92rem; }
.row:last-child{ border-bottom:none; }
.row span:first-child{ color:var(--muted); }
.bar{ height:8px; border-radius:99px; background:rgba(255,255,255,.08); overflow:hidden; margin-top:.4rem; }
@keyframes grow{ from{ width:0; } }
.bar > div{ height:100%; border-radius:99px; animation:grow 1s ease both; }

[data-testid="stSidebar"]{ background:var(--surface); border-right:1px solid var(--border); }

@media (max-width:700px){ .hero h1{ font-size:1.6rem; } .block-container{ padding-left:1rem; padding-right:1rem; } }
@media (prefers-reduced-motion:reduce){ *{ animation:none !important; transition:none !important; } }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def html(s: str):
    """Render HTML without markdown treating indented lines as code."""
    st.markdown("\n".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Lookup tables (same codes as before)
# ----------------------------------------------------------------------------
checking = {"< 0": "A11", "0 - 200": "A12", "> 200": "A13", "No account": "A14"}
history = {
    "No credits / all paid": "A30", "All paid at this bank": "A31",
    "Existing credits paid": "A32", "Past delay": "A33", "Critical account": "A34",
}
savings = {"< 100": "A61", "100 - 500": "A62", "500 - 1000": "A63",
           ">= 1000": "A64", "Unknown / none": "A65"}
employment = {"Unemployed": "A71", "< 1 year": "A72", "1 - 4 years": "A73",
              "4 - 7 years": "A74", ">= 7 years": "A75"}
housing = {"Rent": "A151", "Own": "A152", "For free": "A153"}
purpose = {"Car (new)": "A40", "Car (used)": "A41", "Furniture / equipment": "A42",
           "Radio / TV": "A43", "Appliances": "A44", "Repairs": "A45",
           "Education": "A46", "Retraining": "A48", "Business": "A49", "Other": "A410"}
debtors = {"None": "A101", "Co-applicant": "A102", "Guarantor": "A103"}
prop = {"Real estate": "A121", "Savings / life insurance": "A122",
        "Car or other": "A123", "No property": "A124"}
other_inst = {"Bank": "A141", "Stores": "A142", "None": "A143"}
job = {"Unemployed / unskilled non-resident": "A171", "Unskilled resident": "A172",
       "Skilled employee": "A173", "Management / self-employed": "A174"}
phone = {"None": "A191", "Yes": "A192"}
foreign = {"Yes": "A201", "No": "A202"}
personal_status = {
    "Male: Single": "A93",
    "Female: Divorced / Separated / Married": "A92",
    "Female: Single": "A95",
    "Male: Married / Widowed": "A94",
    "Male: Divorced / Separated": "A91",
}

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💳 Credit Scoring")
    st.caption("CodeAlpha ML Internship · Task 1")
    html("""
    <div class="section-title" style="margin-top:1rem">About the model</div>
    <div class="row"><span>Algorithm</span><span>Random Forest</span></div>
    <div class="row"><span>Dataset</span><span>German Credit (UCI)</span></div>
    <div class="row"><span>Records</span><span>1,000</span></div>
    <div class="row"><span>ROC-AUC</span><span>0.784</span></div>
    <div class="row"><span>Accuracy</span><span>74%</span></div>
    """)
    st.caption("Fill in the applicant details, then press Predict. "
               "The model returns the probability of good credit.")

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
html("""
<div class="hero">
<span class="badge">AI · Risk Assessment</span>
<h1>Credit Scoring Model</h1>
<p>Enter the applicant's details to estimate creditworthiness in seconds.</p>
</div>
""")
st.write("")

# ----------------------------------------------------------------------------
# Form (st.form = no rerun on every widget change -> faster)
# ----------------------------------------------------------------------------
with st.form("applicant_form"):
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="section-title">Loan details</div>', unsafe_allow_html=True)
        age = st.number_input("Age", 18, 80, 35, help="Applicant age in years")
        amount = st.number_input("Credit amount", 250, 20000, 3000, step=100,
                                 help="Requested loan amount")
        duration = st.number_input("Duration (months)", 4, 72, 24,
                                   help="Repayment period")
        installment = st.slider("Installment rate (% of income)", 1, 4, 3,
                                help="Share of disposable income used for repayment")
    with col2:
        st.markdown('<div class="section-title">Financial profile</div>', unsafe_allow_html=True)
        chk = st.selectbox("Checking account", list(checking))
        hist = st.selectbox("Credit history", list(history), index=2)
        sav = st.selectbox("Savings", list(savings))
        emp = st.selectbox("Employment since", list(employment), index=1)
        hous = st.selectbox("Housing", list(housing), index=1)
        pers = st.selectbox("Personal status & gender", list(personal_status), index=0)

    with st.expander("Additional details (optional)"):
        a1, a2, a3 = st.columns(3)
        with a1:
            pur = st.selectbox("Purpose", list(purpose), index=3)
            deb = st.selectbox("Other debtors", list(debtors))
            pro = st.selectbox("Property", list(prop))
            res = st.number_input("Residence since (years)", 1, 4, 2)
        with a2:
            oin = st.selectbox("Other installments", list(other_inst), index=2)
            jb = st.selectbox("Job", list(job), index=2)
            exc = st.number_input("Existing credits", 1, 4, 1)
            dep = st.number_input("Dependents", 1, 2, 1)
        with a3:
            tel = st.selectbox("Telephone", list(phone), index=1)
            frg = st.selectbox("Foreign worker", list(foreign))

    submitted = st.form_submit_button("Predict creditworthiness")

# ----------------------------------------------------------------------------
# Prediction (same model call as before)
# ----------------------------------------------------------------------------
if submitted:
    applicant = {
        "checking_status": checking[chk],
        "duration_months": duration,
        "credit_history": history[hist],
        "purpose": purpose[pur],
        "credit_amount": amount,
        "savings": savings[sav],
        "employment_since": employment[emp],
        "installment_rate": installment,
        "personal_status": personal_status[pers],
        "other_debtors": debtors[deb],
        "residence_since": res,
        "property": prop[pro],
        "age": age,
        "other_installments": other_inst[oin],
        "housing": housing[hous],
        "existing_credits": exc,
        "job": job[jb],
        "dependents": dep,
        "telephone": phone[tel],
        "foreign_worker": foreign[frg],
    }
    with st.status("Analyzing application...", expanded=True) as status:
        st.write("Preparing applicant data")
        st.write("Running the Random Forest model")
        label, proba = predict(applicant)
        status.update(label="Analysis complete", state="complete", expanded=False)
    st.toast("Prediction ready", icon="✅")
    st.session_state["result"] = {
        "label": label, "proba": float(proba), "amount": amount,
        "duration": duration, "monthly": amount / duration, "age": age,
    }

# ----------------------------------------------------------------------------
# Result (kept in session_state so it survives reruns)
# ----------------------------------------------------------------------------
res_state = st.session_state.get("result")
if res_state is None:
    html("""
    <div class="result-wrap"><div class="card" style="text-align:center;color:var(--muted)">
    No prediction yet. Fill in the form above and press <b style="color:var(--text)">Predict</b>.
    </div></div>
    """)
else:
    p = res_state["proba"]
    if p >= 0.70:
        cls, color, risk, icon = "good", "#3ddc97", "Low risk", "✔"
    elif p >= 0.50:
        cls, color, risk, icon = "warn", "#ffc857", "Medium risk", "●"
    else:
        cls, color, risk, icon = "bad", "#ff6b6b", "High risk", "✖"
    circ = 2 * math.pi * 54
    offset = circ * (1 - p)

    st.markdown('<div class="result-wrap"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.4], gap="large")
    with c1:
        html(f"""
        <div class="card" style="text-align:center">
        <div class="gauge">
        <svg width="170" height="170" viewBox="0 0 120 120">
        <circle class="ring-bg" cx="60" cy="60" r="54" fill="none" stroke-width="10"/>
        <circle class="ring" cx="60" cy="60" r="54" fill="none" stroke="{color}" stroke-width="10"
        stroke-dasharray="{circ:.2f}" stroke-dashoffset="{offset:.2f}"/>
        </svg>
        <div class="gauge-center"><div class="gauge-num">{p:.1%}</div><div class="gauge-cap">good credit</div></div>
        </div>
        <div style="margin-top:1rem"><span class="status {cls}">{icon} {res_state['label']}</span></div>
        </div>
        """)
    with c2:
        html(f"""
        <div class="card">
        <div class="kpi-label">Risk assessment</div>
        <div class="kpi-value" style="color:{color}">{risk}</div>
        <div class="bar"><div style="width:{p*100:.1f}%;background:{color}"></div></div>
        <div style="margin-top:1rem">
        <div class="row"><span>Probability of good credit</span><span>{p:.1%}</span></div>
        <div class="row"><span>Probability of bad credit</span><span>{1-p:.1%}</span></div>
        <div class="row"><span>Credit amount</span><span>{res_state['amount']:,}</span></div>
        <div class="row"><span>Duration</span><span>{res_state['duration']} months</span></div>
        <div class="row"><span>Estimated monthly payment</span><span>{res_state['monthly']:,.0f}</span></div>
        </div>
        </div>
        """)