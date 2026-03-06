import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import uuid
import io
import re
import time

from supabase import create_client

# Supabase credentials
SUPABASE_URL = "https://xiiiuexbqddmbchwqyog.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpaWl1ZXhicWRkbWJjaHdxeW9nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3MTA1NTQsImV4cCI6MjA4ODI4NjU1NH0.5Q1jW4nLOImsEGlWsYbp2KfH6PwkH6gjLNl4jiexZuA"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


st.set_page_config(page_title="AI ASD Detection", page_icon="🧠", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    padding-top: 0rem !important;
    background: radial-gradient(circle at top, #0b1020 0, #020617 45%, #020617 100%);
    background-size: 200% 200%;
    animation: bgMove 18s ease-in-out infinite;
}
@keyframes bgMove {
    0% { background-position: 0% 0%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 0%; }
}
.main .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}
@keyframes pulseTitle {
    0% { transform: scale(1); text-shadow: 0 0 8px rgba(244,114,182,0.4), 0 0 18px rgba(124,58,237,0.5); }
    50% { transform: scale(1.05); text-shadow: 0 0 16px rgba(244,114,182,0.9), 0 0 30px rgba(124,58,237,0.9); }
    100% { transform: scale(1); text-shadow: 0 0 8px rgba(244,114,182,0.4), 0 0 18px rgba(124,58,237,0.5); }
}
.app-title { margin: 0; padding: 0.8rem 0; text-align: center; font-size: 2.7rem; font-weight: 900; letter-spacing: 0.05em; background: linear-gradient(90deg,#f472b6,#7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: pulseTitle 2.4s ease-in-out infinite; }
.app-title::after { content: ""; display: block; margin: 0.3rem auto 0 auto; width: 160px; height: 4px; border-radius: 999px; background: linear-gradient(90deg,#f472b6,#7c3aed); }
.card-kid { background: rgba(15, 23, 42, 0.96); border-radius: 20px; padding: 1.6rem; margin: 1rem 0; border: 1px solid rgba(244,114,182,0.8); box-shadow: 0 18px 40px rgba(124,58,237,0.9); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.card-kid:hover { transform: translateY(-3px) scale(1.01); box-shadow: 0 22px 55px rgba(244,114,182,0.95); }
.step-pill { display:inline-block; padding: 0.15rem 0.7rem; border-radius:999px; font-size:0.78rem; font-weight:600; background:rgba(124,58,237,0.18); color:#e9d5ff; margin-bottom:0.25rem; }
.question-text { font-size: 1.05rem; font-weight: 600; color: #e5e7eb; margin-bottom: 0.15rem; }
.hint-text { font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.4rem; }
.legend-row { display:flex; gap:0.5rem; margin:0.3rem 0 0.7rem 0; }
.legend-chip { padding:0.15rem 0.7rem; border-radius:999px; font-size:0.78rem; font-weight:600; }
.legend-ok { background:rgba(34,197,94,0.14); color:#6ee7b7; }
.legend-risk { background:rgba(239,68,68,0.14); color:#fca5a5; }
hr.q-separator { border:0; height:1px; background:linear-gradient(90deg, rgba(124,58,237,0.05), rgba(244,114,182,0.8), rgba(124,58,237,0.05)); margin:0.4rem 0 0.6rem 0; }
.explain-box {
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(244,114,182,0.4);
    border-radius: 12px;
    padding: 0.6rem 0.9rem;
    margin: 0.4rem 0 0.8rem 0;
    font-size: 0.88rem;
    font-weight: 500;
    color: #e9d5ff;
    box-shadow: 0 4px 12px rgba(124,58,237,0.15);
    backdrop-filter: blur(8px);
}
.explain-box::before {
    content: "💡 ";
    font-size: 0.85rem;
}
.scoring-legend {
    background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(16,185,129,0.15));
    border: 1px solid rgba(34,197,94,0.4);
    border-radius: 16px;
    padding: 1rem;
    margin: 0.8rem 0;
    display: flex;
    gap: 1.5rem;
    align-items: center;
    box-shadow: 0 8px 25px rgba(34,197,94,0.2);
}
.scoring-legend .score-0 { color: #10b981; font-weight: 700; font-size: 1.1rem; }
.scoring-legend .score-1 { color: #ef4444; font-weight: 700; font-size: 1.1rem; }
.scoring-desc { font-size: 0.92rem; color: #e5e7eb; line-height: 1.4; }
.stButton > button { border-radius: 999px !important; font-weight: 700 !important; background: linear-gradient(90deg,#f472b6,#7c3aed) !important; color: white !important; border: none !important; box-shadow: 0 12px 30px rgba(244,114,182,0.5) !important; transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease !important; }
.stButton > button:hover { transform: translateY(-2px) scale(1.02) !important; filter: brightness(1.08) !important; box-shadow: 0 16px 40px rgba(124,58,237,0.8) !important; }
.sidebar-card { background: linear-gradient(135deg,#101126,#020617); border-radius: 18px; padding: 1.2rem; border: 1px solid rgba(244,114,182,0.8); box-shadow: 0 12px 30px rgba(124,58,237,0.9); margin-bottom: 0.8rem; }
.sidebar-title { font-size:1.1rem; font-weight:700; color:#f9a8d4; margin-bottom:0.3rem; }
.sidebar-text { color:#e5e7eb; font-size:0.9rem; }
[data-testid="metric-container"] { border-radius: 16px !important; background: rgba(15, 23, 42, 0.95) !important; border: 1px solid rgba(244,114,182,0.8) !important; box-shadow: 0 14px 35px rgba(124,58,237,0.9) !important; }
.risk-low { background: rgba(34,197,94,0.2); color: #10b981; border: 1px solid #10b981; padding: 0.6rem 1.2rem; border-radius: 20px; font-weight: 700; font-size: 1rem; }
.risk-medium { background: rgba(251,191,36,0.2); color: #f59e0b; border: 1px solid #f59e0b; padding: 0.6rem 1.2rem; border-radius: 20px; font-weight: 700; font-size: 1rem; }
.risk-high { background: rgba(239,68,68,0.2); color: #ef4444; border: 1px solid #ef4444; padding: 0.6rem 1.2rem; border-radius: 20px; font-weight: 700; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

# ✅ UPDATED: Clearer Explanations
EXPLANATIONS = {
    "A1": {"en": "Natural eye contact during interaction", "ta": "பேசும்போது கண் பார்வை"},
    "A2": {"en": "Turns head when name called", "ta": "பெயர் சொன்னால் திரும்புதல்"},
    "A3": {"en": "Points to share excitement", "ta": "ஆர்வத்தை விரல் காட்டுதல்"},
    "A4": {"en": "Follows your pointing finger", "ta": "விரல் காட்டினால் பார்த்தல்"},
    "A5": {"en": "Hand flapping or spinning", "ta": "கை அசைவு/சுழன்றல்"},
    "A6": {"en": "Lines up toys in perfect rows", "ta": "பொம்மைகளை வரிசையாக வைத்தல்"},
    "A7": {"en": "Very selective with food", "ta": "உணவு மிகவும் தேர்ந்தெடுக்குதல்"},
    "A8": {"en": "Covers ears at normal sounds", "ta": "சாதாரண சத்தத்திற்கு காதை மூடுதல்"},
    "A9": {"en": "Pretends toys are real", "ta": "பொம்மைகளுடன் கற்பனை விளையாட்டு"},
    "A10": {"en": "Hits age development milestones", "ta": "வயது ஏற்ற வளர்ச்சி"}
}

# TRANSLATIONS
TRANSLATIONS = {
    "en": {
        "app_title": "🧠 AI ASD Detection", "language_select": "Language / மொழி",
        "sidebar_title": "🔐 user authentication", "account_section": "👤 account",
        "full_name": "👤 full name *", "email": "📧 email *", "mobile": "📞 mobile (10 digits) *",
        "password": "🔑 password (8+ chars) *", "login_btn": "✅ login", "register_btn": "➕ register",
        "login_success": "✅ login successful!", "welcome": "👋 welcome", "logout": "🚪 logout",
        "fields_required": "❌ all fields required!", "mobile_invalid": "📞 mobile must be exactly 10 digits!",
        "password_invalid": "🔑 password must be 8+ characters!", "email_exists": "❌ email already registered!",
        "account_not_found": "❌ account not found!", "invalid_credentials": "❌ invalid credentials!",
        "register_success": "✅ Registration complete!", "auth_required": "🔐 please complete authentication!",
        "auth_info": "📱 mobile: 10 digits | 🔑 password: 8+ characters", 
        "how_to_use": "how to use", "how_to_use_desc": "fill form → analyze → download report", 
        "scoring_guide": "scoring guide", "auto_save": "results auto‑saved to backend", 
        "asd_screening": "A1–A10 ASD screening", "scoring_hint": "select your observation",
        "child_details": "Child / Adult details", "age_years": "age (years) *", "age_months": "extra months * (0-12)", 
        "gender": "gender", "blood_group": "🩸 blood group *", "ethnicity": "ethnicity *",
        "jaundice": "jaundice? *", "family_asd": "family ASD? *", "analyze_btn": "🚀 analyze & save", 
        "ai_result": "AI analysis result", "asd_prob": "🧠 ASD probability", "aq_score": "📈 total AQ score",
        "high_risk": "🔴 HIGH RISK", "moderate_risk": "🟡 MODERATE RISK", "low_risk": "🟢 LOW RISK",
        "download_report": "📥 download report", "saved_success": "✅ saved + download ready!",
        "no_concern": "typical", "concern": "concern", "missing_required": "❌ fill required: ",
        "risk_drivers": "Key Risk Drivers",
        "score_0": "✅ 0 = TYPICAL (normal behavior)", 
        "score_1": "⚠️ 1 = CONCERN (ASD indicator)",
        "score_desc": "Mark what you **observe most often**",
        "month_validation": "❌ Months must be 0-12 only!"
    },
    "ta": {
        "app_title": "🧠 AI ASD கண்டறிதல்", "language_select": "மொழி / Language",
        "sidebar_title": "🔐 பயனர் அங்கீகாரம்", "account_section": "👤 கணக்கு",
        "full_name": "👤 முழு பெயர் *", "email": "📧 மின்னஞ்சல் *", "mobile": "📞 மொபைல் *",
        "password": "🔑 பாஸ்வேர்டு *", "login_btn": "✅ உள்நுழை", "register_btn": "➕ பதிவு",
        "login_success": "✅ உள்நுழைவு வெற்றி!", "welcome": "👋 வரவேற்கிறோம்", "logout": "🚪 வெளியேறு",
        "fields_required": "❌ அனைத்தும் தேவை!", "mobile_invalid": "📞 10 இலக்கங்கள்!", 
        "password_invalid": "🔑 8+ எழுத்துகள்!", "email_exists": "❌ மின்னஞ்சல் உள்ளது!",
        "account_not_found": "❌ கணக்கு இல்லை!", "invalid_credentials": "❌ தவறான சான்று!",
        "register_success": "✅ பதிவு முடிந்தது!", "auth_required": "🔐 அங்கீகாரம் செய்யவும்!",
        "auth_info": "📱 10 இலக்கங்கள் | 🔑 8+ எழுத்துகள்", 
        "how_to_use": "எப்படி பயன்படுத்துவது", "how_to_use_desc": "படிவம் → பகுப்பாய்வு → பதிவிறக்க", 
        "scoring_guide": "மதிப்பெண் விளக்கம்", "auto_save": "முடிவுகள் சேமிக்கப்படும்", 
        "asd_screening": "A1-A10 ASD பரிசோதனை", "scoring_hint": "உங்கள் கவனிப்பை தேர்ந்தெடுக்கவும்",
        "child_details": "குழந்தை விவரங்கள்", "age_years": "வயது (வருடங்கள்)*", "age_months": "மாதங்கள் * (0-12)", 
        "gender": "பாலினம்", "blood_group": "🩸 இரத்தகுழு*", "ethnicity": "இனம்*",
        "jaundice": "மஞ்சள் காமாலை?*", "family_asd": "குடும்ப ASD?*", "analyze_btn": "🚀 பகுப்பாய்வு", 
        "ai_result": "AI முடிவு", "asd_prob": "🧠 ASD சாத்தியம்", "aq_score": "📈 AQ மதிப்பெண்",
        "high_risk": "🔴 உயர் ஆபத்து", "moderate_risk": "🟡 மிதமான ஆபத்து", "low_risk": "🟢 குறைந்த ஆபத்து",
        "download_report": "📥 அறிக்கை", "saved_success": "✅ சேமிக்கப்பட்டது!", 
        "no_concern": "சாதாரணம்", "concern": "கவலை", "missing_required": "❌ நிரப்பவும்: ",
        "risk_drivers": "முக்கிய காரணங்கள்",
        "score_0": "✅ 0 = சாதாரணம் (இயல்பான நடத்தை)", 
        "score_1": "⚠️ 1 = கவலை (ASD அறிகுறி)",
        "score_desc": "பெரும்பாலும் **காணப்படுவதை** குறிக்கவும்",
        "month_validation": "❌ மாதங்கள் 0-12 மட்டுமே!"
    }
}

def t(key: str) -> str:
    current_lang = st.session_state.get("lang", "English")
    lang_code = "ta" if current_lang == "தமிழ்" else "en"
    return TRANSLATIONS[lang_code].get(key, key)

def validate_mobile(phone: str) -> bool:
    return bool(re.match(r"^\d{10}$", phone))

def validate_password(pwd: str) -> bool:
    return len(pwd) >= 8

def save_user_response(record):
    """✅ FIXED: Robust backend saving with ALL Q&A answers - ASD PROB AS PERCENTAGE"""
    RESPONSE_FILE = "user_responses.csv"
    
    # ✅ ALL 10 Q&A SCORES + other data
    full_record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user_id": st.session_state["user_id"],
        "user_name": st.session_state["user_info"]["name"],
        "A1": record.get("A1", 0), "A2": record.get("A2", 0), "A3": record.get("A3", 0),
        "A4": record.get("A4", 0), "A5": record.get("A5", 0), "A6": record.get("A6", 0),
        "A7": record.get("A7", 0), "A8": record.get("A8", 0), "A9": record.get("A9", 0),
        "A10": record.get("A10", 0),
        "total_ones": record.get("total_ones", 0),
        "age_years": record.get("age_years", 0),
        "age_months": record.get("age_months", 0),
        "total_months": record.get("total_months", 0),
        "gender": record.get("gender", ""),
        "blood_group": record.get("blood_group", ""),
        "ethnicity": record.get("ethnicity", ""),
        "jaundice": record.get("jaundice", ""),
        "family_asd": record.get("family_asd", ""),
        "asd_probability": record.get("asd_probability", 0.0) * 100,  # ✅ SAVED AS PERCENTAGE (0-100)
        "risk_category": record.get("risk_category", "LOW")
    }
    
    df_record = pd.DataFrame([full_record])
    
    # ✅ ROBUST SAVE: Handle file existence properly
    try:
        if os.path.exists(RESPONSE_FILE):
            existing_df = pd.read_csv(RESPONSE_FILE)
            updated_df = pd.concat([existing_df, df_record], ignore_index=True)
            updated_df.to_csv(RESPONSE_FILE, index=False)
        else:
            df_record.to_csv(RESPONSE_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Save error: {str(e)}")
        return False

def get_age_adjusted_thresholds(total_months):
    if total_months <= 24: return 0.39, 0.74
    elif total_months <= 36: return 0.29, 0.64  
    elif total_months <= 48: return 0.24, 0.54
    elif total_months <= 72: return 0.19, 0.44
    else: return 0.14, 0.34

def get_risk_drivers(a_scores, prob, total_months):
    high_drivers = ["A5", "A6", "A8"]
    social_drivers = ["A1", "A2", "A3", "A4"]
    ones = [k for k,v in a_scores.items() if v == 1]
    
    if prob > 0.34:
        high_matches = [q for q in high_drivers if q in ones]
        return high_matches[:3] if high_matches else ones[:3]  
    elif prob > 0.14 and len(ones) >= 3:
        social_matches = [q for q in social_drivers if q in ones]
        return social_matches[:2] if social_matches else ones[:2]
    return ["None"]

# SESSION STATE
if "lang" not in st.session_state: st.session_state["lang"] = "English"
if "user_id" not in st.session_state: st.session_state["user_id"] = None
if "user_info" not in st.session_state: st.session_state["user_info"] = {}

LOGIN_FILE = "users_login.csv"
USER_COLUMNS = ["timestamp", "user_id", "name", "email", "phone", "password"]

if os.path.exists(LOGIN_FILE):
    try: 
        users_df = pd.read_csv(LOGIN_FILE)
    except: 
        users_df = pd.DataFrame(columns=USER_COLUMNS)
else:
    users_df = pd.DataFrame(columns=USER_COLUMNS)

# HEADER
col_title, col_lang = st.columns([3, 1])
with col_title:
    st.markdown(f'<div class="app-title">{t("app_title")}</div>', unsafe_allow_html=True)
with col_lang:
    sel = st.selectbox(t("language_select"), ["English", "தமிழ்"], 
                      index=0 if st.session_state["lang"] == "English" else 1, key="lang_select")
    st.session_state["lang"] = sel

st.markdown("---")

# SIDEBAR AUTH
with st.sidebar:
    st.markdown(f'<div class="sidebar-card"><div class="sidebar-title">{t("sidebar_title")}</div></div>', unsafe_allow_html=True)
    
    with st.form("auth_form", clear_on_submit=False):
        st.markdown(f"### {t('account_section')}")
        full_name = st.text_input(t("full_name"), placeholder="John Doe")
        email = st.text_input(t("email"), placeholder="example@email.com")
        phone = st.text_input(t("mobile"), placeholder="9876543210")
        password = st.text_input(t("password"), type="password")
        
        c1, c2 = st.columns(2)
        with c1: login_action = st.form_submit_button(t("login_btn"), use_container_width=True)
        with c2: register_action = st.form_submit_button(t("register_btn"), use_container_width=True)

    if login_action:
        if not all([email, phone, password]):
            st.error(t("fields_required"))
        elif users_df.empty or not (users_df["email"].str.lower() == email.lower()).any():
            st.error(t("account_not_found"))
        else:
            user_row = users_df[users_df["email"].str.lower() == email.lower()].iloc[0]
            if str(user_row["password"]) == password and validate_mobile(phone):
                st.success(t("login_success"))
                st.session_state["user_id"] = user_row["user_id"]
                st.session_state["user_info"] = {"name": user_row["name"], "email": user_row["email"], "phone": user_row["phone"]}
                st.rerun()
            else: st.error(t("invalid_credentials"))

    if register_action:
        errors = []
        if not all([full_name.strip(), email.strip(), phone, password]): errors.append(t("fields_required"))
        elif not validate_mobile(phone): errors.append(t("mobile_invalid"))
        elif not validate_password(password): errors.append(t("password_invalid"))
        elif not users_df.empty and (users_df["email"].str.lower() == email.lower()).any(): errors.append(t("email_exists"))
        
        if errors:
            for e in errors: st.error(e)
        else:
            new_id = str(uuid.uuid4())[:8]
            new_row = pd.DataFrame([{
                "timestamp": datetime.now().isoformat(timespec="seconds"), 
                "user_id": new_id,
                "name": full_name.strip(), 
                "email": email.strip().lower(), 
                "phone": phone.strip(), 
                "password": password
            }])
            if os.path.exists(LOGIN_FILE): 
                new_row.to_csv(LOGIN_FILE, mode="a", header=False, index=False)
            else: 
                new_row.to_csv(LOGIN_FILE, index=False)
            st.success(t("register_success"))

    if st.session_state.get("user_id"):
        st.markdown("---")
        ui = st.session_state["user_info"]
        st.markdown(f'<div class="sidebar-card"><div class="sidebar-title">{t("welcome")} {ui["name"]}</div><div class="sidebar-text">📧 {ui["email"]}<br>📞 {ui["phone"]}</div></div>', unsafe_allow_html=True)
        if st.button(t("logout"), use_container_width=True):
            st.session_state["user_id"] = None
            st.session_state["user_info"] = {}
            st.rerun()

# MAIN APP
if st.session_state.get("user_id"):
    QUESTIONS = {
        "A1": {"en": "Eye contact – looks at eyes?", "ta": "முகம் பார்க்கிறாரா?"},
        "A2": {"en": "Name response – turns when called?", "ta": "பெயர் அழைத்தால் பார்க்கிறாரா?"},
        "A3": {"en": "Points to share interest?", "ta": "விரல் காட்டி ஆர்வம் பகிர்கிறாரா?"},
        "A4": {"en": "Follows pointing?", "ta": "காட்டினால் பின்பற்றுகிறாரா?"},
        "A5": {"en": "Repetitive movements?", "ta": "மீண்டும் கை/உடல் அசைவு?"},
        "A6": {"en": "Lines up toys?", "ta": "பொம்மைகளை வரிசைப்படுத்துகிறாரா?"},
        "A7": {"en": "Picky eating?", "ta": "உணவு தேர்வு செய்கிறாரா?"},
        "A8": {"en": "Sound sensitivity?", "ta": "சத்தத்திற்கு அதிக பதில்?"},
        "A9": {"en": "Pretend play?", "ta": "கற்பனை விளையாட்டு?"},
        "A10": {"en": "Age-appropriate milestones?", "ta": "வயது ஏற்ற வளர்ச்சி?"}
    }

    lang_key = "ta" if st.session_state["lang"] == "தமிழ்" else "en"

    # HOW TO USE
    st.markdown(f'<div class="card-kid"><div class="question-text" style="font-size:1.15rem;">🌈 {t("how_to_use")}</div><ul style="color:#e5e7eb;font-size:0.93rem;margin-top:0.3rem;"><li>{t("how_to_use_desc")}</li><li>💾 {t("auto_save")}</li></ul></div>', unsafe_allow_html=True)
    
    # ✅ CRYSTAL CLEAR SCORING LEGEND
    st.markdown(f'''
    <div class="scoring-legend">
        <div>
            <div class="score-0">{t("score_0")}</div>
            <div class="scoring-desc">{t("score_desc")}</div>
        </div>
        <div>
            <div class="score-1">{t("score_1")}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # QUESTIONS SECTION
    st.markdown(f'<div class="card-kid"><div class="question-text" style="font-size:1.15rem;">👶 {t("asd_screening")}</div><div class="hint-text">{t("scoring_hint")}</div></div>', unsafe_allow_html=True)

    a_scores = {}
    for i in range(1, 11):
        key = f"A{i}"
        st.markdown(f"<div class='step-pill'>Step {i}/10</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-text'>Q{i}: {QUESTIONS[key][lang_key]}</div>", unsafe_allow_html=True)
        st.markdown(f'<div class="explain-box">{EXPLANATIONS[key][lang_key]}</div>', unsafe_allow_html=True)
        a_scores[key] = st.slider(f"Score {key}", 0, 1, 0, key=f"{key}_slider", format="%d")
        st.markdown("<hr class='q-separator'>", unsafe_allow_html=True)

    # CHILD DETAILS
    st.markdown(f'<div class="card-kid"><div class="question-text" style="font-size:1.15rem;">👤 {t("child_details")}</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        age_years = st.slider(t("age_years"), 0, 100, 2, help="Years (0-100)")
        age_months = st.slider(t("age_months"), 0, 11, 0, help="Extra months (0-12 ONLY)")  # ✅ FIXED: 0-11
        
        total_months = age_years * 12 + age_months
        age_display = f"{age_years}y {age_months}m ({total_months}mo)" if age_years > 0 or age_months > 0 else "0 months"
        st.markdown(f'<div style="font-size:0.9rem;color:#9ca3af;">📅 {age_display}</div>', unsafe_allow_html=True)
        
        gender = st.selectbox(t("gender"), ["m", "f"])
        blood_group = st.selectbox(t("blood_group"), ["", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    with c2:
        ethnicity = st.selectbox(t("ethnicity"), ["", "?", "Indian", "South Indian", "North Indian", "White-European"])
        jaundice = st.selectbox(t("jaundice"), ["", "?", "no", "yes"])
        family_asd = st.selectbox(t("family_asd"), ["", "?", "no", "yes"])

    if st.button(t("analyze_btn"), use_container_width=True):
        missing = []
        # ✅ FIXED: Proper validation including months 0-12
        if total_months == 0: missing.append("age")
        if age_months > 12: st.error(t("month_validation"))
        if blood_group == "": missing.append("blood group")
        if ethnicity == "": missing.append("ethnicity")
        if jaundice == "": missing.append("jaundice")
        if family_asd == "": missing.append("family ASD")

        if missing or age_months > 12:
            if missing:
                st.error(t("missing_required") + ", ".join(missing))
        else:
            total_ones = sum(a_scores.values())
            low_thresh, high_thresh = get_age_adjusted_thresholds(total_months)
            age_factor = max(0.7, 1.6 - (total_months / 100))
            
            if total_ones >= 5:
                prob = min(0.95, 0.76 + (total_ones-5)*0.04 * age_factor)
            elif total_ones >= 3:
                prob = min(0.65, 0.36 + (total_ones-3)*0.08 * age_factor)
            else:
                prob = min(0.28, 0.07 + total_ones*0.10 * age_factor)
            
            risk_drivers = get_risk_drivers(a_scores, prob, total_months)
            
            # ✅ FIXED: Save ALL Q&A answers to backend
            record = {
                **a_scores,  # All 10 Q&A scores
                "total_ones": total_ones,
                "age_years": age_years, 
                "age_months": age_months, 
                "total_months": total_months,
                "gender": gender, 
                "blood_group": blood_group, 
                "ethnicity": ethnicity,
                "jaundice": jaundice, 
                "family_asd": family_asd, 
                "asd_probability": float(prob),
                "risk_category": "HIGH" if prob > high_thresh else "MEDIUM" if prob > low_thresh else "LOW"
            }
            
            # ✅ SAVE TO BACKEND
            if save_user_response(record):
                st.markdown(f'<div class="card-kid"><div class="question-text" style="font-size:1.15rem;">📊 {t("ai_result")}</div></div>', unsafe_allow_html=True)

                r1, r2, r3, r4 = st.columns(4)
                with r1: 
                    st.metric(t("asd_prob"), f"{prob:.1%}")
                with r2: 
                    st.metric(t("aq_score"), total_ones, delta=f"/10")
                with r3:
                    age_context = f"({total_months}mo: {low_thresh:.0%}-{high_thresh:.0%})"
                    if prob > high_thresh:
                        st.markdown(f'<div class="risk-high">{t("high_risk")}</div>', unsafe_allow_html=True)
                    elif prob > low_thresh:
                        st.markdown(f'<div class="risk-medium">{t("moderate_risk")}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="risk-low">{t("low_risk")}</div>', unsafe_allow_html=True)
                    st.caption(age_context)
                with r4:
                    driver_text = ", ".join(risk_drivers) if risk_drivers and risk_drivers[0] != "None" else "None"
                    st.markdown(f"**{t('risk_drivers')}**: {driver_text}")

                # ✅ DOWNLOAD REPORT WITH ALL Q&A
                buf = io.StringIO()
                df_record = pd.DataFrame([record])
                df_record.to_csv(buf, index=False)
                st.download_button(
                    t("download_report"), buf.getvalue(),
                    file_name=f"asd_report_{st.session_state['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                st.success(t("saved_success"))
            else:
                st.error("Failed to save results!")
else:
    st.warning(t("auth_required"))
    st.info(t("auth_info"))
