# Missing Link - Setup Instructions

Follow these steps to run the application:

## 1. Prerequisites
- Python 3.8 or higher installed.
- C++ Build Tools (required for `dlib`, a dependency of `face_recognition`).

## 2. Environment Setup
Open your terminal in the project directory and run:

**On Windows:**
```powershell
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

Then install the dependencies:
```bash
pip install -r requirements.txt
```

## 3. Running the App
Execute the following command:
```bash
streamlit run app.py
```

## 4. Demo Credentials
- **Admin**: Username: `admin`, Password: `admin123`
- **NGO**: Username: `ngo`, Password: `ngo123`
- **General User**: You can register your own account on the login page.

## 5. Usage Flow
1. **Register User**: Go to the login page and register as a "General User".
2. **Register Child**: Log in and go to "Register Missing Child". Upload a photo and fill in details.
3. **Search**: Go to "Search / Identify", upload a photo of the same person (or a similar one), and see the match result.
4. **NGO Alert**: If a match > 80% is found, click "Generate Alert". Then log in as `ngo` to see the alert and manage the case.
