# Missing Link - Platform Setup Instructions

Missing Link is an AI-powered child identification platform featuring a React/Vite frontend and a FastAPI backend with facial recognition capabilities.

## 1. Prerequisites
- Python 3.8 or higher installed.
- C++ Build Tools (required for `dlib`, a dependency of `face_recognition`).
- Node.js (v16+) and npm.

## 2. Backend Setup (FastAPI)

Open your terminal, navigate to the project directory, and activate your environment:

**On Windows:**
```powershell
.\venv\Scripts\activate
```
**On macOS/Linux:**
```bash
source venv/bin/activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Run the FastAPI backend server:
```bash
cd backend
uvicorn main:app --reload
```
The backend API will run on `http://127.0.0.1:8000`.

## 3. Frontend Setup (React + Vite)

Open a **new** terminal, navigate to the `frontend` folder, and install the npm packages:

```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
```

The frontend application will be available at `http://localhost:5173`.

## 4. Demo Credentials
- **Admin**: Username: `admin`, Password: `admin123`
- **NGO**: Username: `ngo`, Password: `ngo123`
- **General User**: You can register your own account on the login page.

## 5. Usage Flow
1. **Register User**: Go to the login page and register as a "General User".
2. **Register Child**: Log in and go to "Register Missing Child". Upload a photo and fill in details.
3. **Search**: Go to "Search / Identify", upload a photo of the same person (or a similar one), and see the match result.
4. **NGO Alert**: If a match is found with high confidence, an alert is generated. Log in as `ngo` to view and manage cases.
