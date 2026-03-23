import os
import pickle
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import pyotp
from twilio.rest import Client

from database import get_db_connection, init_db
from auth import login_user, register_new_user, create_access_token, verify_token
from ai_engine import get_face_encoding, compare_faces, simulate_age_progression

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "mock_sid")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "mock_token")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "+1234567890")

def send_twilio_sms(to_number: str, message_body: str):
    if TWILIO_ACCOUNT_SID == "mock_sid":
        print(f"\n[MOCK TWILIO SMS] To: {to_number} | Message: {message_body}\n")
        return
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(body=message_body, from_=TWILIO_PHONE_NUMBER, to=to_number)

def make_twilio_call(to_number: str, message_body: str):
    if TWILIO_ACCOUNT_SID == "mock_sid":
        print(f"\n[MOCK TWILIO VOICE CALL] To: {to_number} | Message: {message_body}\n")
        return
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    twiml = f"<Response><Say voice='Polly.Matthew'>{message_body}</Say></Response>"
    client.calls.create(twiml=twiml, from_=TWILIO_PHONE_NUMBER, to=to_number)

app = FastAPI(title="Missing Link API")

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(db_dir, exist_ok=True)
    init_db()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded photos
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
os.makedirs(data_dir, exist_ok=True)
app.mount("/data", StaticFiles(directory=data_dir), name="data")

# --- Pydantic Models ---

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "General User"
    inviteCode: Optional[str] = None

class StatusUpdateRequest(BaseModel):
    status: str

class AlertRequest(BaseModel):
    child_id: int
    confidence: float
    found_photo_path: str
    status: str = "Pending"

class OTPRequest(BaseModel):
    phone: str

security = HTTPBearer()

def require_admin_ngo(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    role = user_data.get("role")
    if role not in ['Admin', 'NGO/Police', 'General User']: # Added General User based on original plan
        raise HTTPException(status_code=403, detail="Forbidden: Admin or NGO/Police role required")
    return role

@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = login_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    token = create_access_token({"id": user["id"], "username": user["username"], "role": user["role"]})
    return {"message": "Success", "user": user, "token": token}

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    admin_code = os.environ.get("ADMIN_INVITE_CODE", "ADMIN123")
    ngo_code = os.environ.get("NGO_INVITE_CODE", "NGO456")
    
    # Strict validation for Admin/NGO roles
    if req.role == "Admin":
        if not req.inviteCode or req.inviteCode != admin_code:
            raise HTTPException(status_code=403, detail="Invalid Invite Code for this role.")
    elif req.role == "NGO/Police":
        if not req.inviteCode or req.inviteCode != ngo_code:
            raise HTTPException(status_code=403, detail="Invalid Invite Code for this role.")
    else:
        # Force "General User" for anything else or if role was tampered with in request
        req.role = "General User"
        
    if register_new_user(req.username, req.password, req.role):
        user = login_user(req.username, req.password)
        if user:
            token = create_access_token({"id": user["id"], "username": user["username"], "role": user["role"]})
            return {"message": "Registration successful", "user": user, "token": token}
        
    raise HTTPException(status_code=400, detail="Username already exists")

# --- Dashboard & Stats ---

@app.get("/api/stats")
def get_stats(role: str = Depends(require_admin_ngo)):
    conn = get_db_connection()
    total_missing = conn.execute("SELECT COUNT(*) FROM missing_children").fetchone()[0]
    total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    reunited = conn.execute("SELECT COUNT(*) FROM matches WHERE status = 'Reunited'").fetchone()[0]
    
    recent_alerts = conn.execute('''
        SELECT a.*, c.name, m.confidence 
        FROM alerts a 
        JOIN matches m ON a.match_id = m.id
        JOIN missing_children c ON m.child_id = c.id
        ORDER BY a.created_at DESC LIMIT 3
    ''').fetchall()
    
    conn.close()
    return {
        "metrics": {
            "active_cases": total_missing,
            "potential_matches": total_matches,
            "reunited": reunited
        },
        "recent_activity": [dict(a) for a in recent_alerts]
    }

# --- Child Registration & Cases ---

@app.post("/api/children/send-otp")
def send_otp(req: OTPRequest):
    totp = pyotp.TOTP(pyotp.random_base32())
    otp_code = totp.now() # 6-digit code
    
    conn = get_db_connection()
    conn.execute("INSERT INTO otps (phone, otp_code) VALUES (?, ?)", (req.phone, otp_code))
    conn.commit()
    conn.close()
    
    msg = f"Your Missing Link verification code is: {otp_code}."
    send_twilio_sms(req.phone, msg)
    return {"message": "OTP sent successfully"}

@app.post("/api/children/register")
async def register_child(
    name: str = Form(...),
    age: int = Form(...),
    location: str = Form(...),
    date_missing: str = Form(...),
    guardian_contact: str = Form(...),
    guardian_phone: str = Form(...),
    otp_code: str = Form(...),
    photo: UploadFile = File(...),
    role: str = Depends(require_admin_ngo)
):
    conn = get_db_connection()
    
    # 1. Verify OTP
    otp_record = conn.execute(
        "SELECT id FROM otps WHERE phone = ? AND otp_code = ? ORDER BY created_at DESC LIMIT 1",
        (guardian_phone, otp_code)
    ).fetchone()
    
    if not otp_record:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid OTP or phone number")
        
    # Clean up OTP so it can't be reused
    conn.execute("DELETE FROM otps WHERE id = ?", (otp_record['id'],))
    conn.commit()
    photo_bytes = await photo.read()
    safe_name = name.replace(' ', '_')
    photo_filename = f"{safe_name}_{photo.filename}"
    photo_path = os.path.join(data_dir, photo_filename)
    
    with open(photo_path, "wb") as f:
        f.write(photo_bytes)
        
    encoding = get_face_encoding(photo_bytes)
    if encoding is None:
        raise HTTPException(status_code=400, detail="No face detected in the image")
        
    encoding_blob = pickle.dumps(encoding)
    db_photo_path = f"data/{photo_filename}" # relative for static mount
    
    conn.execute('''
        INSERT INTO missing_children (name, age, location, date_missing, guardian_contact, guardian_phone, is_verified, photo_path, face_encoding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, location, date_missing, guardian_contact, guardian_phone, 1, db_photo_path, encoding_blob))
    conn.commit()
    conn.close()
    
    return {"message": "Child registered successfully. Guardian phone verified via OTP."}

@app.get("/api/cases")
def get_cases(search: Optional[str] = None, role: str = Depends(require_admin_ngo)):
    conn = get_db_connection()
    if search:
        query = "SELECT * FROM missing_children WHERE name LIKE ? OR location LIKE ?"
        cases = conn.execute(query, (f'%{search}%', f'%{search}%')).fetchall()
    else:
        cases = conn.execute("SELECT * FROM missing_children").fetchall()
        
    cases_list = []
    for case in cases:
        c_dict = dict(case)
        del c_dict['face_encoding'] # Don't send blob to frontend
        
        match_info = conn.execute('''
            SELECT status FROM matches WHERE child_id = ? ORDER BY id DESC LIMIT 1
        ''', (case['id'],)).fetchone()
        
        c_dict['status'] = match_info['status'] if match_info else "No Matches"
        cases_list.append(c_dict)
        
    conn.close()
    return {"cases": cases_list}

@app.put("/api/cases/{child_id}/status")
def update_case_status(child_id: int, req: StatusUpdateRequest, role: str = Depends(require_admin_ngo)):
    conn = get_db_connection()
    conn.execute("UPDATE matches SET status = ? WHERE child_id = ?", (req.status, child_id))
    conn.commit()
    conn.close()
    return {"message": f"Status updated to {req.status}"}

# --- Search & Identification ---

@app.post("/api/search")
async def search_child(photo: UploadFile = File(...)):
    photo_bytes = await photo.read()
    
    # Save uploaded search photo temporarily (or permanently for matches)
    search_filename = f"search_{photo.filename}"
    search_path = os.path.join(data_dir, search_filename)
    with open(search_path, "wb") as f:
        f.write(photo_bytes)
    db_search_path = f"data/{search_filename}"
        
    found_encoding = get_face_encoding(photo_bytes)
    if found_encoding is None:
        raise HTTPException(status_code=400, detail="Could not extract facial features")
        
    conn = get_db_connection()
    cases = conn.execute("SELECT id, name, age, location, guardian_phone, photo_path, face_encoding FROM missing_children").fetchall()
    
    known_encodings = []
    case_ids = []
    for case in cases:
        if case['face_encoding']:
            known_encodings.append(pickle.loads(case['face_encoding']))
            case_ids.append(case['id'])
            
    if not known_encodings:
        conn.close()
        return {"matches": [], "message": "No cases registered in database"}
        
    raw_matches = compare_faces(found_encoding, known_encodings)
    
    result_matches = []
    for idx, confidence in raw_matches:
        case_id = case_ids[idx]
        case_data = next(dict(c) for c in cases if c['id'] == case_id)
        del case_data['face_encoding']
        
        # Simulate age progression
        years_missing = 2
        # Use absolute path for cv2 in the backend function
        abs_original_path = os.path.join(os.path.dirname(__file__), '..', case_data['photo_path'])
        
        aged_abs_path = simulate_age_progression(abs_original_path, years_missing)
        aged_db_path = None
        if aged_abs_path and os.path.exists(aged_abs_path):
            aged_db_path = f"data/{os.path.basename(aged_abs_path)}"
            
        result_matches.append({
            "child": case_data,
            "confidence": confidence,
            "aged_photo_path": aged_db_path,
            "found_photo_path": db_search_path
        })
        
        # Twilio Alerts Trigger for High Match Confidence!
        if confidence > 85.0:
            guardian_phone = case_data.get('guardian_phone')
            if guardian_phone:
                sms_msg = f"ALERT: Missing child '{case_data['name']}' has been identified with {confidence:.1f}% match probability. Please log in to Missing Link for details."
                voice_msg = f"Alert from Missing Link. A potential high confidence match was found for {case_data['name']}."
                
                # Send SMS and Call to Guardian
                send_twilio_sms(guardian_phone, sms_msg)
                make_twilio_call(guardian_phone, voice_msg)
                
                # Send SMS to Police (Mocking a central police num for this feature)
                POLICE_NUMBER = "+1911000000"
                pol_msg = f"POLICE DISPATCH: High confidence match ({confidence:.1f}%) for missing child '{case_data['name']}' discovered by Missing Link."
                send_twilio_sms(POLICE_NUMBER, pol_msg)
        
    conn.close()
    return {"matches": result_matches}

# --- Alerts System ---

@app.post("/api/alerts")
def generate_alert(req: AlertRequest):
    conn = get_db_connection()
    
    case_name = conn.execute("SELECT name FROM missing_children WHERE id = ?", (req.child_id,)).fetchone()
    if not case_name:
        raise HTTPException(status_code=404, detail="Child not found")
        
    name = case_name[0]
    alert_prefix = "HIGH CONFIDENCE" if req.confidence > 80 else "MANUAL REVIEW"
    
    conn.execute("INSERT INTO matches (child_id, confidence, status, found_photo_path) VALUES (?, ?, ?, ?)",
                 (req.child_id, req.confidence, req.status, req.found_photo_path))
    match_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    alert_msg = f"{alert_prefix}: {req.confidence:.1f}% match for {name}"
    conn.execute("INSERT INTO alerts (match_id, message) VALUES (?, ?)", (match_id, alert_msg))
    
    conn.commit()
    conn.close()
    return {"message": "Alert generated successfully"}

@app.get("/api/alerts")
def get_alerts(is_read: int = 0, role: str = Depends(require_admin_ngo)):
    conn = get_db_connection()
    alerts = conn.execute('''
        SELECT a.*, c.name, m.confidence, m.found_photo_path, c.photo_path as original_photo
        FROM alerts a 
        JOIN matches m ON a.match_id = m.id
        JOIN missing_children c ON m.child_id = c.id
        WHERE a.is_read = ?
        ORDER BY a.created_at DESC
    ''', (is_read,)).fetchall()
    conn.close()
    return {"alerts": [dict(a) for a in alerts]}

@app.put("/api/alerts/{alert_id}/read")
def mark_alert_read(alert_id: int, role: str = Depends(require_admin_ngo)):
    conn = get_db_connection()
    conn.execute("UPDATE alerts SET is_read = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return {"message": "Alert marked as read"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
