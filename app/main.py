import streamlit as st
import joblib
import numpy as np
import time
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(dotenv_path="../.env")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="VitalSense AI — Smart Health Screening",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- SESSION STATE (NAVIGATION + THEME) ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "disease" not in st.session_state:
    st.session_state.disease = None
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def go_to(page_name, disease=None):
    st.session_state.page = page_name
    if disease:
        st.session_state.disease = disease
    st.rerun()

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# ---------------- THEME COLORS ----------------
if st.session_state.theme == "dark":
    C = {
        "bg": "#0F172A",
        "text": "#F1F5F9",
        "muted": "#94A3B8",
        "card_bg": "#1E293B",
        "card_border": "#334155",
        "sidebar_bg": "#111827",
        "input_bg": "#1E293B",
        "risk_high_bg": "#3F1D1D",
        "risk_high_text": "#FCA5A5",
        "risk_high_border": "#7F1D1D",
        "risk_low_bg": "#0F2E1F",
        "risk_low_text": "#86EFAC",
        "risk_low_border": "#166534",
        "suggestion_bg": "#1E293B",
    }
else:
    C = {
        "bg": "#FFFFFF",
        "text": "#1F2937",
        "muted": "#6B7280",
        "card_bg": "#F9FAFB",
        "card_border": "#E5E7EB",
        "sidebar_bg": "#F3F4F6",
        "input_bg": "#FFFFFF",
        "risk_high_bg": "#FEE2E2",
        "risk_high_text": "#B91C1C",
        "risk_high_border": "#FCA5A5",
        "risk_low_bg": "#DCFCE7",
        "risk_low_text": "#15803D",
        "risk_low_border": "#86EFAC",
        "suggestion_bg": "#F8FAFC",
    }

# ---------------- CUSTOM CSS + ANIMATIONS ----------------
st.markdown(f"""
<style>
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 0 0 rgba(185, 28, 28, 0.4); }}
        70% {{ box-shadow: 0 0 0 16px rgba(185, 28, 28, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(185, 28, 28, 0); }}
    }}
    @keyframes popIn {{
        0% {{ transform: scale(0.85); opacity: 0; }}
        60% {{ transform: scale(1.03); opacity: 1; }}
        100% {{ transform: scale(1); }}
    }}
    @keyframes slideInLeft {{
        from {{ opacity: 0; transform: translateX(-25px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    @keyframes floatUpDown {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-8px); }}
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* ---- Center the top loading/running indicator ---- */
    div[data-testid="stStatusWidget"] {{
        position: fixed !important;
        top: 8px !important;
        left: 50% !important;
        right: auto !important;
        transform: translateX(-50%) !important;
        z-index: 9999 !important;
    }}

    /* ---- App-wide theme colors ---- */
    .stApp {{
        background-color: {C["bg"]};
        color: {C["text"]};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {C["sidebar_bg"]};
    }}
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {{
        color: {C["text"]};
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        animation: fadeInUp 0.7s ease;
        background-color: {C["card_bg"]};
        border-color: {C["card_border"]} !important;
    }}
    input, textarea, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: {C["input_bg"]} !important;
        color: {C["text"]} !important;
    }}

    .hero-title {{
        font-size: 3.4rem;
        font-weight: 900;
        background: linear-gradient(270deg, #4F46E5, #06B6D4, #4F46E5);
        background-size: 600% 600%;
        animation: gradientShift 6s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }}
    .hero-icon {{
        text-align: center;
        font-size: 4rem;
        animation: floatUpDown 3s ease-in-out infinite;
        margin-bottom: 10px;
    }}
    .hero-tagline {{
        text-align: center;
        color: {C["text"]};
        font-size: 1.25rem;
        font-weight: 500;
        margin-bottom: 8px;
        animation: fadeInUp 0.8s ease;
    }}
    .hero-sub {{
        text-align: center;
        color: {C["muted"]};
        font-size: 1rem;
        margin-bottom: 35px;
        animation: fadeInUp 1s ease;
    }}
    .feature-card {{
        background: {C["card_bg"]};
        border: 1px solid {C["card_border"]};
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        animation: fadeInUp 0.8s ease;
        height: 100%;
    }}
    .feature-card h4 {{
        margin-top: 10px;
        margin-bottom: 6px;
        color: {C["text"]};
    }}
    .feature-card p {{
        color: {C["muted"]};
        font-size: 0.9rem;
    }}
    .disease-card {{
        background: {C["card_bg"]};
        border: 2px solid {C["card_border"]};
        border-radius: 18px;
        padding: 28px;
        text-align: center;
        animation: popIn 0.5s ease;
        transition: all 0.25s ease;
        height: 100%;
    }}
    .disease-card:hover {{
        border-color: #4F46E5;
        transform: translateY(-4px);
        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.15);
    }}
    .disease-icon {{
        font-size: 3rem;
        margin-bottom: 10px;
    }}
    .section-title {{
        font-size: 2rem;
        font-weight: 800;
        text-align: center;
        color: {C["text"]};
        margin-bottom: 6px;
        animation: fadeInUp 0.6s ease;
    }}
    .section-sub {{
        text-align: center;
        color: {C["muted"]};
        margin-bottom: 30px;
        animation: fadeInUp 0.7s ease;
    }}
    div[data-testid="stMetric"] {{
        background: {C["card_bg"]};
        border: 1px solid {C["card_border"]};
        border-radius: 12px;
        padding: 15px;
        animation: fadeInUp 0.6s ease;
    }}
    .stButton>button {{
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 10px 24px;
        border: none;
        width: 100%;
        transition: all 0.25s ease;
    }}
    .stButton>button:hover {{
        transform: scale(1.03);
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.45);
    }}
    .stButton>button:active {{
        transform: scale(0.97);
    }}
    .result-card {{
        padding: 22px;
        border-radius: 14px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 15px;
        animation: popIn 0.5s ease;
    }}
    .risk-high {{
        background: {C["risk_high_bg"]};
        color: {C["risk_high_text"]};
        border: 2px solid {C["risk_high_border"]};
        animation: popIn 0.5s ease, pulseGlow 2s ease infinite;
    }}
    .risk-low {{
        background: {C["risk_low_bg"]};
        color: {C["risk_low_text"]};
        border: 2px solid {C["risk_low_border"]};
    }}
    .suggestion-box {{
        background: {C["suggestion_bg"]};
        border-left: 4px solid #4F46E5;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 14px;
        animation: slideInLeft 0.5s ease;
        color: {C["text"]};
    }}
    .suggestion-box li {{
        margin-bottom: 6px;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- THEME TOGGLE (top of every page) ----------------
top_spacer, top_toggle = st.columns([6, 1])
with top_toggle:
    icon = "🌙 Dark" if st.session_state.theme == "light" else "☀️ Light"
    if st.button(icon, key="theme_toggle"):
        toggle_theme()
        st.rerun()

# =========================================================
# PAGE 1: HOME
# =========================================================
if st.session_state.page == "home":
    st.markdown('<div class="hero-icon">🩺</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">VitalSense AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-tagline">Smart, Instant Health Risk Screening Powered by Machine Learning</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Assess your risk for Heart Disease, Diabetes, and Kidney Disease in under a minute — plus get an AI Health Assistant to answer your questions.</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([3, 1, 3])
    with col_b:
        if st.button("🚀 Get Started", key="start_btn"):
            go_to("select")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            '<div class="feature-card"><div style="font-size:2rem;">⚡</div>'
            '<h4>Instant Results</h4><p>Get your risk assessment in seconds using trained ML models.</p></div>',
            unsafe_allow_html=True
        )
    with f2:
        st.markdown(
            '<div class="feature-card"><div style="font-size:2rem;">🎯</div>'
            '<h4>Multi-Disease Coverage</h4><p>Screens for Heart Disease, Diabetes, and Kidney Disease in one place.</p></div>',
            unsafe_allow_html=True
        )
    with f3:
        st.markdown(
            '<div class="feature-card"><div style="font-size:2rem;">💬</div>'
            '<h4>AI Health Assistant</h4><p>Ask follow-up questions and get personalized guidance instantly.</p></div>',
            unsafe_allow_html=True
        )

# =========================================================
# PAGE 2: DISEASE SELECTION
# =========================================================
elif st.session_state.page == "select":
    st.markdown('<div class="section-title">Choose a Screening</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Select the health condition you would like to assess</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="disease-card"><div class="disease-icon">❤️</div>'
            f'<h4>Heart Disease</h4><p style="color:{C["muted"]}; font-size:0.9rem;">Evaluate cardiovascular risk based on clinical indicators.</p></div>',
            unsafe_allow_html=True
        )
        if st.button("Start Heart Screening", key="heart_select"):
            go_to("assess", "Heart Disease")
    with c2:
        st.markdown(
            f'<div class="disease-card"><div class="disease-icon">🩸</div>'
            f'<h4>Diabetes</h4><p style="color:{C["muted"]}; font-size:0.9rem;">Check your likelihood of diabetes from key health metrics.</p></div>',
            unsafe_allow_html=True
        )
        if st.button("Start Diabetes Screening", key="diabetes_select"):
            go_to("assess", "Diabetes")
    with c3:
        st.markdown(
            f'<div class="disease-card"><div class="disease-icon">🫘</div>'
            f'<h4>Kidney Disease</h4><p style="color:{C["muted"]}; font-size:0.9rem;">Assess kidney function risk using lab-based parameters.</p></div>',
            unsafe_allow_html=True
        )
        if st.button("Start Kidney Screening", key="kidney_select"):
            go_to("assess", "Kidney Disease")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅ Back to Home", key="back_home_1"):
        go_to("home")

# =========================================================
# PAGE 3: ASSESSMENT
# =========================================================
elif st.session_state.page == "assess":
    disease = st.session_state.disease

    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown(f'<div class="section-title" style="text-align:left;">{disease} Screening</div>', unsafe_allow_html=True)
    with top_right:
        if st.button("⬅ Change", key="change_disease"):
            go_to("select")

    prediction = None
    prob = None

    # ---------------- HEART DISEASE ----------------
    if disease == "Heart Disease":
        model = joblib.load("../models/heart_model.pkl")

        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                age = st.number_input("Age", 1, 120, 40)
                sex = st.selectbox("Sex", ["Male", "Female"])
                cp = st.selectbox("Chest Pain Type", [0, 1, 2, 3],
                                   help="0: Typical Angina, 1: Atypical Angina, 2: Non-anginal Pain, 3: Asymptomatic")
                fbs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", ["No", "Yes"])
            with col2:
                trestbps = st.number_input("Resting Blood Pressure", 80, 250, 120)
                chol = st.number_input("Cholesterol (mg/dl)", 100, 600, 200)
                restecg = st.selectbox("Resting ECG Result", [0, 1, 2])
                thalach = st.number_input("Max Heart Rate Achieved", 60, 220, 150)
            with col3:
                exang = st.selectbox("Exercise Induced Angina", ["No", "Yes"])
                oldpeak = st.number_input("ST Depression (Oldpeak)", 0.0, 10.0, 1.0, step=0.1)
                slope = st.selectbox("Slope of ST Segment", [0, 1, 2])
                ca = st.selectbox("Number of Major Vessels", [0, 1, 2, 3, 4])
                thal = st.selectbox("Thalassemia Type", [0, 1, 2],
                                     help="0: Normal, 1: Fixed Defect, 2: Reversible Defect")

        if st.button("🔍 Analyze My Risk", key="predict_heart"):
            with st.spinner("Analyzing your health data..."):
                time.sleep(0.8)
                sex_val = 1 if sex == "Male" else 0
                fbs_val = 1 if fbs == "Yes" else 0
                exang_val = 1 if exang == "Yes" else 0

                input_data = np.array([[age, sex_val, cp, trestbps, chol, fbs_val,
                                         restecg, thalach, exang_val, oldpeak,
                                         slope, ca, thal]])

                prediction = model.predict(input_data)[0]
                prob = model.predict_proba(input_data)[0][1]
                st.session_state.prediction = prediction
                st.session_state.prob = prob
                st.session_state.result_disease = disease

    # ---------------- DIABETES ----------------
    elif disease == "Diabetes":
        model = joblib.load("../models/diabetes_model.pkl")

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                pregnancies = st.number_input("Number of Pregnancies", 0, 20, 1)
                glucose = st.number_input("Glucose Level", 0, 300, 120)
                bp = st.number_input("Blood Pressure", 0, 200, 70)
                skin = st.number_input("Skin Thickness (mm)", 0, 100, 20)
            with col2:
                insulin = st.number_input("Insulin Level", 0, 900, 80)
                bmi = st.number_input("BMI", 0.0, 70.0, 25.0, step=0.1)
                dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, 0.5, step=0.01)
                age = st.number_input("Age", 1, 120, 30)

        if st.button("🔍 Analyze My Risk", key="predict_diabetes"):
            with st.spinner("Analyzing your health data..."):
                time.sleep(0.8)
                input_data = np.array([[pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]])
                prediction = model.predict(input_data)[0]
                prob = model.predict_proba(input_data)[0][1]
                st.session_state.prediction = prediction
                st.session_state.prob = prob
                st.session_state.result_disease = disease

    # ---------------- KIDNEY DISEASE ----------------
    elif disease == "Kidney Disease":
        model = joblib.load("../models/kidney_model.pkl")

        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                age = st.number_input("Age", 1, 120, 40)
                bp = st.number_input("Blood Pressure", 0, 200, 80)
                sg = st.number_input("Specific Gravity", 1.000, 1.030, 1.020, step=0.001, format="%.3f")
                al = st.selectbox("Albumin Level", [0, 1, 2, 3, 4, 5])
                su = st.selectbox("Sugar Level", [0, 1, 2, 3, 4, 5])
                rbc = st.selectbox("Red Blood Cells", ["normal", "abnormal"])
                pc = st.selectbox("Pus Cell", ["normal", "abnormal"])
                pcc = st.selectbox("Pus Cell Clumps", ["notpresent", "present"])
            with col2:
                ba = st.selectbox("Bacteria", ["notpresent", "present"])
                bgr = st.number_input("Blood Glucose Random", 0, 500, 120)
                bu = st.number_input("Blood Urea", 0, 400, 40)
                sc = st.number_input("Serum Creatinine", 0.0, 20.0, 1.0, step=0.1)
                sod = st.number_input("Sodium", 0, 200, 140)
                pot = st.number_input("Potassium", 0.0, 15.0, 4.5, step=0.1)
                hemo = st.number_input("Hemoglobin", 0.0, 20.0, 13.0, step=0.1)
            with col3:
                pcv = st.number_input("Packed Cell Volume", 0, 60, 40)
                wc = st.number_input("White Blood Cell Count", 0, 20000, 8000)
                rc = st.number_input("Red Blood Cell Count", 0.0, 8.0, 5.0, step=0.1)
                htn = st.selectbox("Hypertension", ["no", "yes"])
                dm = st.selectbox("Diabetes Mellitus", ["no", "yes"])
                cad = st.selectbox("Coronary Artery Disease", ["no", "yes"])
                appet = st.selectbox("Appetite", ["good", "poor"])
                pe = st.selectbox("Pedal Edema", ["no", "yes"])
                ane = st.selectbox("Anemia", ["no", "yes"])

        if st.button("🔍 Analyze My Risk", key="predict_kidney"):
            with st.spinner("Analyzing your health data..."):
                time.sleep(0.8)
                rbc_v = 1 if rbc == "normal" else 0
                pc_v = 1 if pc == "normal" else 0
                pcc_v = 1 if pcc == "present" else 0
                ba_v = 1 if ba == "present" else 0
                htn_v = 1 if htn == "yes" else 0
                dm_v = 1 if dm == "yes" else 0
                cad_v = 1 if cad == "yes" else 0
                appet_v = 1 if appet == "poor" else 0
                pe_v = 1 if pe == "yes" else 0
                ane_v = 1 if ane == "yes" else 0

                input_data = np.array([[age, bp, sg, al, su, rbc_v, pc_v, pcc_v, ba_v,
                                         bgr, bu, sc, sod, pot, hemo, pcv, wc, rc,
                                         htn_v, dm_v, cad_v, appet_v, pe_v, ane_v]])
                prediction = model.predict(input_data)[0]
                prob = model.predict_proba(input_data)[0][1]
                st.session_state.prediction = prediction
                st.session_state.prob = prob
                st.session_state.result_disease = disease

    # ---------------- SUGGESTIONS DATA ----------------
    SUGGESTIONS = {
        "Heart Disease": {
            "high": [
                "Schedule a check-up with a cardiologist as soon as possible.",
                "Reduce salt and saturated fat intake in your daily diet.",
                "Avoid smoking and limit alcohol consumption.",
                "Start light physical activity only after medical clearance.",
                "Monitor your blood pressure and cholesterol regularly."
            ],
            "low": [
                "Keep up regular physical activity — at least 30 minutes a day.",
                "Maintain a balanced diet rich in fruits, vegetables, and whole grains.",
                "Get routine health check-ups once a year.",
                "Manage stress through relaxation techniques or hobbies.",
                "Keep monitoring blood pressure and cholesterol periodically."
            ]
        },
        "Diabetes": {
            "high": [
                "Consult an endocrinologist or physician for a detailed evaluation.",
                "Monitor blood glucose levels regularly.",
                "Reduce intake of refined sugar and processed carbohydrates.",
                "Incorporate at least 30 minutes of daily exercise.",
                "Maintain a healthy body weight."
            ],
            "low": [
                "Continue a balanced diet with controlled sugar intake.",
                "Stay physically active with regular exercise.",
                "Get periodic blood sugar screening, especially if there's a family history.",
                "Maintain a healthy BMI.",
                "Stay hydrated and avoid sugary beverages."
            ]
        },
        "Kidney Disease": {
            "high": [
                "Consult a nephrologist for further kidney function tests.",
                "Reduce sodium and protein intake as advised by a doctor.",
                "Stay well hydrated, but follow fluid intake guidance from your doctor.",
                "Monitor blood pressure and blood sugar closely, as both affect kidney health.",
                "Avoid overuse of painkillers (NSAIDs) without medical advice."
            ],
            "low": [
                "Stay well hydrated throughout the day.",
                "Maintain a balanced, low-sodium diet.",
                "Keep blood pressure and blood sugar within healthy ranges.",
                "Go for periodic kidney function check-ups.",
                "Avoid unnecessary or prolonged use of painkillers."
            ]
        }
    }

    # ---------------- SHOW RESULT ----------------
    if "prediction" in st.session_state and st.session_state.get("result_disease") == disease:
        prediction = st.session_state.prediction
        prob = st.session_state.prob
        st.markdown("### 📊 Screening Result")

        if disease == "Kidney Disease":
            is_risk = (prediction == 0)
        else:
            is_risk = (prediction == 1)

        confidence = prob * 100 if is_risk else (1 - prob) * 100

        rcol1, rcol2 = st.columns([1, 2])
        with rcol1:
            st.metric(
                label="Risk Level",
                value="High Risk" if is_risk else "Low Risk",
                delta=f"{confidence:.1f}% confidence"
            )
        with rcol2:
            progress_bar = st.progress(0)
            for pct in range(0, int(confidence) + 1, 5):
                progress_bar.progress(min(pct, 100) / 100)
                time.sleep(0.01)

        if is_risk:
            st.markdown(
                f'<div class="result-card risk-high">⚠️ High Risk Detected — {confidence:.1f}% confidence<br>'
                f'<span style="font-size:0.95rem; font-weight:400;">Please consult a healthcare professional for further evaluation.</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="result-card risk-low">✅ Low Risk — {confidence:.1f}% confidence<br>'
                f'<span style="font-size:0.95rem; font-weight:400;">Keep maintaining a healthy lifestyle!</span></div>',
                unsafe_allow_html=True
            )
            st.balloons()

        tips = SUGGESTIONS[disease]["high"] if is_risk else SUGGESTIONS[disease]["low"]
        tips_html = "".join([f"<li>{tip}</li>" for tip in tips])
        st.markdown(
            f'<div class="suggestion-box">'
            f'<strong>💡 {"Recommended Next Steps" if is_risk else "Health Tips to Maintain This"}</strong>'
            f'<ul>{tips_html}</ul>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.caption("⚕️ This result is generated by a Machine Learning model and is not a medical diagnosis. Always consult a certified doctor for medical decisions.")

        # ---------------- AI HEALTH ASSISTANT CHATBOT ----------------
        if st.session_state.get("chat_disease") != disease:
            st.session_state.chat_history = []
            st.session_state.chat_disease = disease

        st.markdown("---")
        st.markdown("### 💬 Ask VitalSense AI Assistant")
        st.caption("Ask questions about your result — e.g. 'Why is this risk high?' or 'What foods should I avoid?'")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_question = st.chat_input("Type your question here...")

        if user_question:
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.write(user_question)

            context = (
                f"The user just completed a {disease} risk screening. "
                f"Result: {'High Risk' if is_risk else 'Low Risk'} "
                f"with {confidence:.1f}% confidence. "
                f"Answer the user's question as a friendly, knowledgeable health assistant. "
                f"Keep the answer concise (3-5 sentences), simple to understand, and always "
                f"remind them this is not a medical diagnosis if giving health advice."
            )

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "user", "content": f"{context}\n\nUser question: {user_question}"}
                        ],
                        max_tokens=400
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)

            st.session_state.chat_history.append({"role": "assistant", "content": answer})