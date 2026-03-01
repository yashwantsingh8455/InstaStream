import streamlit as st
import sqlite3
import os
import hashlib
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="InstaStream Pro", layout="wide", page_icon="📸")

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def apply_custom_css():
    is_dark = st.session_state.theme == 'dark'
    bg = "#000000" if is_dark else "#FAFAFA"
    card_bg = "#121212" if is_dark else "#FFFFFF"
    text = "#FFFFFF" if is_dark else "#262626"
    border = "#262626" if is_dark else "#DBDBDB"
    
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg}; color: {text}; }}
        [data-testid="stSidebar"] {{ background-color: {card_bg}; border-right: 1px solid {border}; }}
        .post-card {{
            background-color: {card_bg};
            border: 1px solid {border};
            border-radius: 12px;
            margin-bottom: 25px;
            overflow: hidden;
        }}
        .post-header {{ padding: 12px; display: flex; align-items: center; font-weight: bold; }}
        .avatar {{ width: 32px; height: 32px; border-radius: 50%; background: #444; margin-right: 10px; }}
        .stButton>button {{ border-radius: 8px; font-weight: 600; }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_css()

# --- 2. DATABASE ENGINE ---
def get_db():
    conn = sqlite3.connect('insta_realtime.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, username TEXT, caption TEXT, img_path TEXT, time DATETIME)')
    c.execute('CREATE TABLE IF NOT EXISTS likes (post_id INTEGER, username TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS comments (post_id INTEGER, username TEXT, comment TEXT)')
    conn.commit()
    return conn, c

conn, c = get_db()

# --- 3. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<h1 style='text-align:center; font-family:cursive;'>InstaStream</h1>", unsafe_allow_html=True)
        mode = st.tabs(["Login", "Sign Up"])
        with mode[0]:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
            if st.button("Log In", use_container_width=True):
                h_p = hashlib.sha256(p.encode()).hexdigest()
                res = c.execute('SELECT * FROM users WHERE username=? AND password=?', (u, h_p)).fetchone()
                if res:
                    st.session_state.logged_in, st.session_state.user = True, u
                    st.rerun()
                else: st.error("Invalid Username or Password")
        with mode[1]:
            nu = st.text_input("New Username", key="reg_u")
            np = st.text_input("New Password", type="password", key="reg_p")
            if st.button("Create Account", use_container_width=True):
                try:
                    c.execute('INSERT INTO users VALUES (?,?)', (nu, hashlib.sha256(np.encode()).hexdigest()))
                    conn.commit()
                    st.success("Registration Successful! Please Login.")
                except: st.error("Username already taken!")

# --- 4. MAIN INTERFACE ---
else:
    with st.sidebar:
        st.markdown(f"<h2 style='font-family:cursive;'>InstaStream</h2>", unsafe_allow_html=True)
        st.write(f"Logged in as: **@{st.session_state.user}**")
        nav = st.radio("Menu", ["🏠 Home", "📸 Create Post", "👤 Profile", "⚙️ Settings", "🛡️ Admin Panel"])
        st.write("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# --- ADMIN PANEL (SECRET LOGIN) ---
    if nav == "🛡️ Admin Panel":
        st.title("🛡️ Admin Gateway")
        if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
        
        if not st.session_state.admin_auth:
            key = st.text_input("Enter Secret Admin Key", type="password")
            if st.button("Verify Identity"):
                if key == "123": # Aapka secret password
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.error("Access Denied!")
        else:
            if st.button("Exit Admin Mode"):
                st.session_state.admin_auth = False
                st.rerun()
            
            # Dashboard Metrics
            total_u = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            total_p = c.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Total Users", total_u)
            col_m2.metric("Total Posts", total_p)
            
            st.write("---")
            st.subheader("👤 Complete User Database")
            
            # Yahan humne 'password' column ko bhi SELECT kiya hai
            user_data = c.execute('SELECT rowid, username, password FROM users').fetchall()
            
            # Create a professional table using Pandas
            import pandas as pd
            admin_df = pd.DataFrame(user_data, columns=['ID', 'Username', 'Hashed Password'])
            
            # Displaying the table with passwords
            st.dataframe(admin_df, use_container_width=True)
            
            st.info("💡 Note: Passwords SHA-256 format mein encrypted hain security ke liye.")

            # Quick Delete Action
            st.subheader("🗑️ Danger Zone")
            user_to_del = st.selectbox("Select user to remove", [u[1] for u in user_data if u[1] != 'admin'])
            if st.button("Delete Account Permanently", type="primary"):
                c.execute('DELETE FROM users WHERE username=?', (user_to_del,))
                conn.commit()
                st.success(f"User @{user_to_del} has been removed.")
                st.rerun()

    # --- HOME FEED ---
    elif nav == "🏠 Home":
        col_main, col_side = st.columns([2, 1])
        with col_main:
            st.subheader("Latest Posts")
            all_posts = c.execute('SELECT * FROM posts ORDER BY time DESC').fetchall()
            for p in all_posts:
                p_id, p_user, p_cap, p_img, p_time = p
                with st.container():
                    st.markdown(f"""<div class="post-card">
                        <div class="post-header"><div class="avatar"></div>@{p_user}</div>
                    </div>""", unsafe_allow_html=True)
                    if os.path.exists(p_img): st.image(p_img, use_container_width=True)
                    
                    # Real-time Interactions
                    likes = c.execute('SELECT COUNT(*) FROM likes WHERE post_id=?', (p_id,)).fetchone()[0]
                    if st.button(f"❤️ {likes} Likes", key=f"lk_{p_id}"):
                        check = c.execute('SELECT * FROM likes WHERE post_id=? AND username=?', (p_id, st.session_state.user)).fetchone()
                        if not check:
                            c.execute('INSERT INTO likes VALUES (?,?)', (p_id, st.session_state.user))
                            conn.commit()
                            st.rerun()
                    
                    st.markdown(f"**@{p_user}** {p_cap}")
                    with st.expander("View Comments"):
                        comments = c.execute('SELECT username, comment FROM comments WHERE post_id=?', (p_id,)).fetchall()
                        for cm in comments: st.write(f"**@{cm[0]}**: {cm[1]}")
                        new_cm = st.text_input("Add comment...", key=f"tc_{p_id}")
                        if st.button("Post", key=f"bc_{p_id}"):
                            c.execute('INSERT INTO comments VALUES (?,?,?)', (p_id, st.session_state.user, new_cm))
                            conn.commit()
                            st.rerun()
                st.divider()
        
        with col_side:
            st.markdown("### Suggested for you")
            others = c.execute('SELECT username FROM users WHERE username != ? LIMIT 4', (st.session_state.user,)).fetchall()
            for o in others:
                st.write(f"**@{o[0]}**")
                st.button("Follow", key=f"fol_{o[0]}")

    # --- CREATE POST ---
    elif nav == "📸 Create Post":
        st.header("Share a Moment")
        f = st.file_uploader("Upload Image", type=['jpg','png','jpeg'])
        cap = st.text_area("Caption")
        if st.button("Share Post", use_container_width=True):
            if f:
                if not os.path.exists("uploads"): os.makedirs("uploads")
                path = f"uploads/{st.session_state.user}_{datetime.now().strftime('%M%S')}_{f.name}"
                with open(path, "wb") as img_file: img_file.write(f.getbuffer())
                c.execute('INSERT INTO posts (username, caption, img_path, time) VALUES (?,?,?,?)', (st.session_state.user, cap, path, datetime.now()))
                conn.commit()
                st.success("Live!")
                st.rerun()

    # --- SETTINGS ---
    elif nav == "⚙️ Settings":
        st.header("Settings")
        st.session_state.theme = st.selectbox("Theme Mode", ["dark", "light"], index=0 if st.session_state.theme == 'dark' else 1)
        if st.button("Save Changes"):
            st.rerun()