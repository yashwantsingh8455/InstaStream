import streamlit as st
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# --- PAGE CONFIG ---
st.set_page_config(page_title="InstaPro MOD Dashboard", layout="wide")

# --- CUSTOM INSTA THEMES ---
st.sidebar.header("🎨 Instagram Theme Mod")
theme_choice = st.sidebar.selectbox(
    "Select Theme:",
    ["Insta Dark Mode", "Insta Light Mode", "Classic Blue", "Neon Hacker"]
)

themes = {
    "Insta Dark Mode": {"bg": "#000000", "text": "#FFFFFF", "accent": "#E1306C", "sidebar": "#121212"},
    "Insta Light Mode": {"bg": "#FFFFFF", "text": "#262626", "accent": "#0095F6", "sidebar": "#FAFAFA"},
    "Classic Blue": {"bg": "#F0F2F5", "text": "#1C1E21", "accent": "#1877F2", "sidebar": "#FFFFFF"},
    "Neon Hacker": {"bg": "#0D0208", "text": "#00FF41", "accent": "#FF0055", "sidebar": "#101010"}
}

selected = themes[theme_choice]

# CSS Injection
st.markdown(f"""
    <style>
    .stApp {{ background-color: {selected['bg']}; color: {selected['text']}; }}
    [data-testid="stSidebar"] {{ background-color: {selected['sidebar']}; border-right: 1px solid #333; }}
    .stButton>button {{ background-color: {selected['accent']}; color: white !important; font-weight: bold; border-radius: 8px; width: 100%; border: none; }}
    h1, h2, h3, h4, h5, h6, p, span, label, .stMetric {{ color: {selected['text']} !important; }}
    .stTextInput>div>div>input {{ background-color: {selected['sidebar']}; color: {selected['text']}; border: 1px solid {selected['accent']}; }}
    </style>
    """, unsafe_allow_html=True)

# --- UI INTERFACE ---
st.title(f"📸 Instagram MOD: {theme_choice}")
st.write(f"System User: **{os.getlogin()}**")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🌐 Instagram Live Feed")
    st.info("Launch karne se pehle saare Chrome windows band kar dein!")
    launch_btn = st.button("🚀 Launch Official Instagram")
    st.image("https://img.freepik.com/free-vector/instagram-icon_1057-2227.jpg", width=100)

with col2:
    st.subheader("🕵️ External Features")
    target_user = st.text_input("Track User Status:", placeholder="Type username...")
    enable_tracking = st.toggle("Enable Live Tracking")
    
    st.divider()
    st.subheader("📥 Downloader Mod")
    st.button("Download Last Post/Story")

# --- BACKEND ACTION ---
if launch_btn:
    if not target_user:
        st.error("Bhai, pehle target username toh daal do!")
    else:
        chrome_options = Options()
        pc_user = os.getlogin()
        
        # Session Path
        profile = f"C:\\Users\\{pc_user}\\AppData\\Local\\Google\\Chrome\\User Data"
        chrome_options.add_argument(f"user-data-dir={profile}")
        # 'Tracker' profile agar banaya hai toh, warna 'Default' use karein
        chrome_options.add_argument("profile-directory=Default") 
        
        # Crash se bachne ke liye zaruri arguments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            st.info("Chrome launch ho raha hai... Wait karein.")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            # Instagram open karein
            driver.get("https://www.instagram.com/direct/inbox/")
            st.success(f"Tracking Start: {target_user}")

            if enable_tracking:
                status_placeholder = st.empty()
                while True:
                    try:
                        # User search logic
                        user_el = driver.find_element(By.XPATH, f"//span[contains(text(), '{target_user}')]")
                        user_el.click()
                        time.sleep(3)
                        
                        status = driver.find_element(By.XPATH, "//header//span[contains(text(), 'Active')]").text
                        status_placeholder.metric("Current Status", status)
                        st.toast(f"{target_user} is {status}!")
                    except:
                        status_placeholder.metric("Current Status", "Offline/Unknown")
                    
                    time.sleep(60)
                    driver.refresh()
                    time.sleep(5)
            else:
                st.warning("Tracking Toggle OFF hai, sirf browser khula rahega.")
                while True: time.sleep(10) # Browser khula rakhne ke liye

        except Exception as e:
            if "DevToolsActivePort" in str(e):
                st.error("❌ CHROME ERROR: Aapka Chrome pehle se khula hai! Task Manager se band karein.")
            else:
                st.error(f"❌ Error: {e}")
        finally:
            try: driver.quit()
            except: pass