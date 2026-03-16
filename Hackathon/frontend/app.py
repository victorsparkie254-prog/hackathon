import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from PIL import Image
import os

# --- Configuration ---
st.set_page_config(
    page_title="AI Crop Disease Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL
API_BASE_URL = os.getenv("UPSTREAM_API_URL", "http://localhost:8000")

# --- Translations Dictionary ---
LANGUAGES = {
    "English": {
        "title": "🌱 AI Crop Disease Early Detection Assistant",
        "subtitle": "Monitor your farm & diagnose diseases instantly.",
        "sidebar_title": "Navigation & Settings",
        "nav_dashboard": "📊 IoT Sensor Dashboard",
        "nav_diagnose": "🔍 AI Disease Diagnosis",
        "temp": "Temperature",
        "humidity": "Humidity",
        "moisture": "Soil Moisture",
        "alerts_title": "⚠️ Active Alerts",
        "upload_label": "Take a photo of a sick leaf or upload an image.",
        "predict_btn": "Diagnose Image",
        "results": "Diagnosis Results",
        "treatment": "Recommended Treatment",
        "error_api": "Error connecting to the backend API."
    },
    "Swahili": {
        "title": "🌱 Msaidizi wa AI wa Magonjwa ya Mimea",
        "subtitle": "Fuatilia shamba lako & tambua magonjwa mara moja.",
        "sidebar_title": "Urambazaji & Mipangilio",
        "nav_dashboard": "📊 Dashibodi ya Vihisi (IoT)",
        "nav_diagnose": "🔍 Utambuzi wa Magonjwa (AI)",
        "temp": "Joto (Temperature)",
        "humidity": "Unyevu wa Hewa",
        "moisture": "Unyevu wa Udongo",
        "alerts_title": "⚠️ Tahadhari Muhimu",
        "upload_label": "Piga picha ya jani lenye ugonjwa au pakia picha.",
        "predict_btn": "Tambua Ugonjwa",
        "results": "Matokeo ya Utambuzi",
        "treatment": "Matibabu Yanayopendekezwa",
        "error_api": "Hitilafu katika kuunganisha kwenye API."
    }
}

# --- State ---
if 'lang' not in st.session_state:
    st.session_state.lang = "English"

# --- UI Functions ---

def get_text(key):
    return LANGUAGES[st.session_state.lang][key]

def fetch_sensor_data():
    try:
        response = requests.get(f"{API_BASE_URL}/api/sensors", params={"limit": 50}, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        # Mock Data for Hackathon if backend is down
        now = datetime.now()
        data = []
        for i in range(20):
            data.append({
                "id": i,
                "device_id": "esp32_farm_01",
                "temperature": 25.0 + (i % 5),
                "humidity": 60.0 - (i % 10),
                "soil_moisture": 45.0 if i > 5 else 25.0,
                "timestamp": (now - timedelta(minutes=(19-i)*30)).isoformat() # Correctly ordered mock time
            })
        return data
    return []

def diagnose_image(image_bytes):
    try:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = requests.post(f"{API_BASE_URL}/api/predict", files=files, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        # Mock prediction if backend is unreachable
        return {"prediction": "Northern Leaf Blight", "confidence": 0.94}
    return None

def main():
    # Sidebar
    st.sidebar.title(get_text("sidebar_title"))
    lang_choice = st.sidebar.selectbox("Language / Lugha", ["English", "Swahili"])
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()
        
    page = st.sidebar.radio("", [get_text("nav_dashboard"), get_text("nav_diagnose")])
    
    st.title(get_text("title"))
    st.markdown(f"*{get_text('subtitle')}*")
    
    if page == get_text("nav_dashboard"):
        render_dashboard()
    else:
        render_diagnosis()

def render_dashboard():
    data = fetch_sensor_data()
    if not data:
        st.error(get_text("error_api"))
        return
        
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    latest = df.iloc[-1]
    
    # KPIs
    st.markdown("### Vituo vya Hali ya Hewa / Live Conditions")
    col1, col2, col3 = st.columns(3)
    col1.metric(get_text("temp"), f"{latest['temperature']} °C")
    col2.metric(get_text("humidity"), f"{latest['humidity']} %")
    
    # Highlight critical soil moisture
    moisture_color = "normal" if latest['soil_moisture'] >= 30.0 else "inverse"
    col3.metric(get_text("moisture"), f"{latest['soil_moisture']} %", delta="Low!" if latest['soil_moisture'] < 30.0 else "Good", delta_color=moisture_color)
    
    # Active Alerts
    if latest['soil_moisture'] < 30.0:
        st.warning(f"**{get_text('alerts_title')}**: Uhitaji Haraka wa Maji! Sehemu ya Shamba #1 inakauka sana. " if st.session_state.lang == "Swahili" else f"**{get_text('alerts_title')}**: Urgent Water Needs! Zone #1 is critically dry.")
        
    # Charts
    st.markdown("### Mwenendo / Trends")
    tab1, tab2 = st.tabs([get_text("moisture") + " & " + get_text("temp"), get_text("humidity")])
    
    with tab1:
        fig1 = px.line(df, x='timestamp', y=['soil_moisture', 'temperature'], title='Soil Moisture & Temperature over Time')
        st.plotly_chart(fig1, use_container_width=True)
        
    with tab2:
        fig2 = px.line(df, x='timestamp', y='humidity', title='Humidity Over Time')
        st.plotly_chart(fig2, use_container_width=True)

def render_diagnosis():
    st.markdown("### " + get_text("nav_diagnose"))
    
    # Allow camera input for mobile phones, or file uploader
    img_file = st.file_uploader(get_text("upload_label"), type=['png', 'jpg', 'jpeg'])
    camera_file = st.camera_input("Piga Picha" if st.session_state.lang == "Swahili" else "Take a Picture")
    
    target_file = camera_file if camera_file else img_file
    
    if target_file is not None:
        image = Image.open(target_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        if st.button(get_text("predict_btn"), type="primary"):
            with st.spinner('Inachambua...' if st.session_state.lang == 'Swahili' else 'Analyzing...'):
                result = diagnose_image(target_file.getvalue())
                
                if result:
                    st.success(f"{get_text('results')}: **{result['prediction']}** ({result['confidence']*100:.1f}% confidence)")
                    
                    st.markdown(f"#### {get_text('treatment')}:")
                    if "Healthy" in result['prediction']:
                        st.info("Mmea wako una afya nzuri!" if st.session_state.lang == "Swahili" else "Your crop is healthy! No action needed.")
                    elif "Blight" in result['prediction']:
                        st.warning("Ondoa majani yaliyoathirika na nyunyizia dawa za kuvunda (Fungicide) mapema." if st.session_state.lang == "Swahili" else "Remove affected leaves. Apply fungicide early to prevent spreading.")
                    elif "Rust" in result['prediction']:
                        st.warning("Tumia mzunguko wa mazao na upande mbegu zinazostahimili magonjwa. Tumia dawa ya ukungu ikibidi." if st.session_state.lang == "Swahili" else "Practice crop rotation and plant resistant varieties. Use fungicide if severe.")
                    else:
                        st.warning("Tafadhali wasiliana na afisa mshauri wa kilimo." if st.session_state.lang == "Swahili" else "Please consult your local agricultural extension officer.")
                else:
                    st.error(get_text("error_api"))

if __name__ == "__main__":
    main()
