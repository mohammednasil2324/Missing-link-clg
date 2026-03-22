import streamlit as st
import pandas as pd
from PIL import Image
import os
import io
import pickle

from database import get_db_connection, init_db
from auth import login_user, register_new_user
from ai_engine import get_face_encoding, compare_faces, simulate_age_progression

# Page Configuration
st.set_page_config(page_title="Missing Link - AI Child Identification", layout="wide")

# Custom CSS for premium humanitarian theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main { 
        background-color: #f8fbff; 
    }
    
    .stApp {
        background: radial-gradient(circle at top left, #f0f7ff, #ffffff);
    }

    /* Professional Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e1e8f0;
    }
    
    /* Header Styles */
    .header-container {
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        border-bottom: 2px solid #0056b3;
    }
    
    .header-style { 
        color: #004085; 
        font-weight: 600; 
        letter-spacing: -0.5px;
        font-size: 2.2rem !important;
        margin-bottom: 0px !important;
    }
    
    /* Cards and Containers */
    .card { 
        background-color: #ffffff; 
        padding: 1.5rem; 
        border-radius: 16px; 
        border: 1px solid #eef2f8;
        box-shadow: 0 4px 20px rgba(0, 86, 179, 0.05); 
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 86, 179, 0.08);
    }
    
    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: #0056b3;
        font-weight: 600;
    }
    
    /* Button Styling */
    .stButton>button { 
        background: linear-gradient(135deg, #0056b3 0%, #007bff 100%); 
        color: #ffffff; 
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 4px 15px rgba(0, 86, 179, 0.3);
    }
    
    /* Confidence Labels */
    .confidence-high {
        color: #d93025;
        background-color: #fce8e6;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    .confidence-manual {
        color: #e37400;
        background-color: #fef7e0;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }

    /* Image Styling */
    .stImage > img {
        border-radius: 12px;
        border: 1px solid #eef2f8;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Initialize DB on first run
if not os.path.exists("data"):
    os.makedirs("data")
init_db()

def login_page():
    st.markdown("<h1 class='header-style'>Missing Link: AI-Powered Child Identification</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid credentials")
                
    with col2:
        st.subheader("Register")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        role = st.selectbox("Role", ["General User", "NGO/Police", "Admin"])
        if st.button("Register"):
            if register_new_user(new_user, new_pass, role):
                st.success("Account created! You can now login.")
            else:
                st.error("Username already exists.")

def dashboard():
    st.sidebar.title(f"Role: {st.session_state.user['role']}")
    st.sidebar.write(f"Logged in as: {st.session_state.user['username']}")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    menu = ["Dashboard", "Register Missing Child", "Search / Identify", "Alerts"]
    if st.session_state.user['role'] in ["NGO/Police", "Admin"]:
        menu.append("Manage Cases")
    if st.session_state.user['role'] == "Admin":
        menu.append("System Statistics")
        
    choice = st.sidebar.radio("Menu", menu)

    if choice == "Dashboard":
        show_stats()
    elif choice == "Register Missing Child":
        register_child_ui()
    elif choice == "Search / Identify":
        search_ui()
    elif choice == "Alerts":
        alerts_ui()
    elif choice == "Manage Cases":
        manage_cases_ui()
    elif choice == "System Statistics":
        system_stats_ui()

def show_stats():
    st.markdown("<h2 style='color:#004085; margin-bottom:1.5rem;'>Mission Overview</h2>", unsafe_allow_html=True)
    
    conn = get_db_connection()
    total_missing = conn.execute("SELECT COUNT(*) FROM missing_children").fetchone()[0]
    total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    reunited = conn.execute("SELECT COUNT(*) FROM matches WHERE status = 'Reunited'").fetchone()[0]
    
    # Metrics Row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class='card'>
            <p style='color:#6c757d; font-size:0.9rem; margin-bottom:5px;'>ACTIVE CASES</p>
            <h2 style='margin:0; color:#0056b3;'>{total_missing}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='card'>
            <p style='color:#6c757d; font-size:0.9rem; margin-bottom:5px;'>POTENTIAL MATCHES</p>
            <h2 style='margin:0; color:#28a745;'>{total_matches}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='card'>
            <p style='color:#6c757d; font-size:0.9rem; margin-bottom:5px;'>SUCCESSFULLY REUNITED</p>
            <h2 style='margin:0; color:#6f42c1;'>{reunited}</h2>
        </div>
        """, unsafe_allow_html=True)

    # Recent Alerts Section
    st.markdown("<h3 style='color:#004085; margin-top:2rem;'>Recent Activity</h3>", unsafe_allow_html=True)
    recent_alerts = conn.execute('''
        SELECT a.*, c.name, m.confidence 
        FROM alerts a 
        JOIN matches m ON a.match_id = m.id
        JOIN missing_children c ON m.child_id = c.id
        ORDER BY a.created_at DESC LIMIT 3
    ''').fetchall()
    
    if recent_alerts:
        for alert in recent_alerts:
            color = "#d93025" if alert['confidence'] > 80 else "#e37400"
            st.markdown(f"""
            <div style='background-color:white; padding:1rem; border-radius:12px; border-left:4px solid {color}; margin-bottom:0.8rem; box-shadow:0 2px 10px rgba(0,0,0,0.03);'>
                <p style='margin:0; font-size:0.85rem; color:#6c757d;'>{alert['created_at']}</p>
                <p style='margin:0; font-weight:600;'>{alert['message']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent alerts found.")
        
    conn.close()

def register_child_ui():
    st.header("Register a Missing Child")
    with st.form("registration_form"):
        name = st.text_input("Child's Name")
        age = st.number_input("Age", min_value=0, max_value=18)
        location = st.text_input("Last Seen Location")
        date_missing = st.date_input("Date Missing")
        guardian = st.text_input("Guardian Contact Info")
        photo = st.file_uploader("Upload Photo", type=['jpg', 'png', 'jpeg'])
        
        submit = st.form_submit_state = st.form_submit_button("Register Case")
        
        if submit and photo:
            # Save photo
            img = Image.open(photo)
            photo_path = f"data/{name.replace(' ', '_')}_{photo.name}"
            img.save(photo_path)
            
            # Get encoding
            encoding = get_face_encoding(photo_path)
            if encoding is not None:
                encoding_blob = pickle.dumps(encoding)
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO missing_children (name, age, location, date_missing, guardian_contact, photo_path, face_encoding)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, age, location, str(date_missing), guardian, photo_path, encoding_blob))
                conn.commit()
                conn.close()
                st.success(f"Case for {name} registered successfully with face encoding.")
            else:
                st.warning("Could not detect a face in the image. Please try another photo.")

def search_ui():
    st.header("Identify a Found Child")
    photo = st.file_uploader("Upload Photo of found child", type=['jpg', 'png', 'jpeg'])
    
    if photo:
        st.image(photo, width=300, caption="Preview")
        if st.button("Search Database"):
            # Get found child encoding
            found_encoding = get_face_encoding(photo.read())
            
            if found_encoding is not None:
                conn = get_db_connection()
                cases = conn.execute("SELECT * FROM missing_children").fetchall()
                
                known_encodings = []
                case_ids = []
                for case in cases:
                    if case['face_encoding']:
                        known_encodings.append(pickle.loads(case['face_encoding']))
                        case_ids.append(case['id'])
                
                if not known_encodings:
                    st.info("No cases registered in the database yet.")
                    conn.close()
                    return

                matches = compare_faces(found_encoding, known_encodings)
                
                matches_with_db_ids = []
                for idx, confidence in matches:
                    matches_with_db_ids.append((case_ids[idx], confidence))
                
                st.session_state.current_matches = matches_with_db_ids
                st.session_state.current_photo_read = photo.getvalue()
                conn.close()
            else:
                st.error("Could not extract facial features from the uploaded photo.")
                
        # Display matches outside the button condition to prevent state loss
        if 'current_matches' in st.session_state and st.session_state.current_matches:
            matches = st.session_state.current_matches
            conn = get_db_connection()
            cases = conn.execute("SELECT * FROM missing_children").fetchall()
            
            st.markdown(f"<h3 style='color:#004085; margin-top:2rem;'>Found {len(matches)} Potential Matches</h3>", unsafe_allow_html=True)
            for case_idx, confidence in matches:
                case_data = next(c for c in cases if c['id'] == case_idx)
                
                years_missing = 2 # Placeholder logic
                aged_path = simulate_age_progression(case_data['photo_path'], years_missing)

                with st.container(border=True):
                    # Header info
                    st.markdown(f"""
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <h3 style='margin:0; color:#0056b3;'>{case_data['name']}</h3>
                            <span class='{"confidence-high" if confidence > 80 else "confidence-manual"}'>
                                {confidence:.1f}% Confidence
                            </span>
                        </div>
                        <p style='margin-bottom:15px; color:#6c757d;'>Last seen: {case_data['location']} | Age: {case_data['age']}</p>
                    """, unsafe_allow_html=True)
                    
                    st.progress(min(confidence/100, 1.0))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.image(case_data['photo_path'], caption="Original Photo", use_container_width=True)
                    with c2:
                        if aged_path and os.path.exists(aged_path):
                            st.image(aged_path, caption=f"Aged Simulation (+{years_missing}y)", use_container_width=True)

                    # Action button
                    if st.button(f"Generate Official Alert for {case_data['name']}", key=f"alert_{case_idx}"):
                        alert_prefix = "HIGH CONFIDENCE" if confidence > 80 else "MANUAL REVIEW"
                        conn.execute("INSERT INTO matches (child_id, confidence, status, found_photo_path) VALUES (?, ?, ?, ?)",
                                     (case_data['id'], confidence, 'Pending', case_data['photo_path']))
                        match_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                        alert_msg = f"{alert_prefix}: {confidence:.1f}% match for {case_data['name']}"
                        conn.execute("INSERT INTO alerts (match_id, message) VALUES (?, ?)",
                                     (match_id, alert_msg))
                        conn.commit()
                        st.toast(f"Alert generated for {case_data['name']}!", icon="🚨")
            conn.close()
        elif 'current_matches' in st.session_state and not st.session_state.current_matches:
             st.warning("No matches found in the database. Please check the photo quality.")

def alerts_ui():
    st.markdown("<h2 style='color:#004085; margin-bottom:1.5rem;'>Alerts Board</h2>", unsafe_allow_html=True)
    conn = get_db_connection()
    
    tab1, tab2 = st.tabs(["🆕 New Alerts", "✅ Archive"])
    
    def render_alerts(is_read):
        alerts = conn.execute('''
            SELECT a.*, c.name, m.confidence, m.found_photo_path, c.photo_path as original_photo
            FROM alerts a 
            JOIN matches m ON a.match_id = m.id
            JOIN missing_children c ON m.child_id = c.id
            WHERE a.is_read = ?
            ORDER BY a.created_at DESC
        ''', (is_read,)).fetchall()
        
        if not alerts:
            st.info("No alerts in this category.")
            return

        for alert in alerts:
            color = "#d93025" if alert['confidence'] > 80 else "#e37400"
            with st.container(border=True):
                st.markdown(f"""
                    <div style='display:flex; justify-content:space-between; border-left:5px solid {color}; padding-left: 10px;'>
                        <h4 style='margin:0;'>{alert['message']}</h4>
                        <span style='color:#6c757d; font-size:12px;'>{alert['created_at']}</span>
                    </div>
                    <p style='color:#6c757d; font-size:14px; margin-top:5px; margin-left:15px;'>Confidence: {alert['confidence']:.1f}%</p>
                """, unsafe_allow_html=True)
                
                # Show photos in alert for quick verification
                c1, c2 = st.columns(2)
                with c1:
                    st.image(alert['original_photo'], caption="Registered Photo", width=150)
                with c2:
                    st.image(alert['found_photo_path'], caption="Match Photo", width=150)

                if not is_read:
                    if st.button("Resolve / Mark as Read", key=f"read_{alert['id']}"):
                        conn.execute("UPDATE alerts SET is_read = 1 WHERE id = ?", (alert['id'],))
                        conn.commit()
                        st.toast("Alert archived successfully.")
                        st.rerun()

    with tab1:
        render_alerts(0)
    with tab2:
        render_alerts(1)
        
    conn.close()

def manage_cases_ui():
    st.markdown("<h2 style='color:#004085; margin-bottom:1.5rem;'>Case Management</h2>", unsafe_allow_html=True)
    conn = get_db_connection()
    
    # Filter/Search for cases
    search_query = st.text_input("Search cases by name or location...")
    
    query = "SELECT * FROM missing_children"
    params = ()
    if search_query:
        query += " WHERE name LIKE ? OR location LIKE ?"
        params = (f'%{search_query}%', f'%{search_query}%')
    
    cases = conn.execute(query, params).fetchall()
    
    if not cases:
        st.info("No matching cases found.")
    else:
        # Display as professional table/list
        for case in cases:
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 4, 2])
                
                with col1:
                    st.image(case['photo_path'], width=100)
                
                with col2:
                    st.markdown(f"""
                    <h4 style='margin:0; color:#0056b3;'>{case['name']} (Age: {case['age']})</h4>
                    <p style='margin:0; font-size:14px; color:#6c757d;'>Last Seen: {case['location']} on {case['date_missing']}</p>
                    <p style='margin:0; font-size:14px; color:#6c757d;'>Contact: {case['guardian_contact']}</p>
                    """, unsafe_allow_html=True)
                
                with col3:
                    # Current status of matches for this child
                    match_info = conn.execute('''
                        SELECT status FROM matches WHERE child_id = ? ORDER BY id DESC LIMIT 1
                    ''', (case['id'],)).fetchone()
                    
                    status = match_info['status'] if match_info else "No Matches"
                    st.markdown(f"<p style='margin-bottom:5px;'>Status: <b>{status}</b></p>", unsafe_allow_html=True)
                    
                    if st.button("Update Status", key=f"manage_{case['id']}"):
                        st.session_state.selected_case_id = case['id']
                        st.session_state.show_update_modal = True
                
                # Conditional "Modal" (Streamlit style)
                if 'selected_case_id' in st.session_state and st.session_state.selected_case_id == case['id']:
                    st.divider()
                    new_status = st.selectbox("Assign New Status", 
                                             ["Pending", "Verified", "Found", "Reunited"],
                                             key=f"new_status_{case['id']}")
                    if st.button("Save Changes", key=f"save_{case['id']}"):
                        conn.execute("UPDATE matches SET status = ? WHERE child_id = ?", (new_status, case['id']))
                        conn.commit()
                        st.toast(f"Status for {case['name']} updated to {new_status}!")
                        del st.session_state.selected_case_id
                        st.rerun()
    
    conn.close()

def system_stats_ui():
    st.header("Admin Panel - System Stats")
    conn = get_db_connection()
    users = conn.execute("SELECT username, role FROM users").fetchall()
    st.subheader("Manage Users")
    st.table(pd.DataFrame([dict(u) for u in users]))
    
    # Simple table of all registered children
    st.subheader("All Registered Cases")
    children = conn.execute("SELECT name, age, location, date_missing FROM missing_children").fetchall()
    st.table(pd.DataFrame([dict(c) for c in children]))
    conn.close()

# Main Flow Control
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
