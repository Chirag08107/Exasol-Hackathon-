# FormSahay

An AI assistant that guides users through Indian government forms (PAN, Aadhaar, passport, driving license, and more) via a chat interface, backed by an 80-form knowledge base in Exasol, and generates a correctly filled PDF for the user to review and submit themselves.
A demonstration video of the website can be found at this link - https://drive.google.com/file/d/1LCilKTxe7FwVeizETi2lHCCraRwlXJgB/view?usp=sharing

PPT of the idea - https://docs.google.com/presentation/d/1Ub9r1B9Dg4DOkabrbVfrBajf8WSNpobx/edit?usp=sharing&ouid=114585485842855005793&rtpof=true&sd=true

## Prerequisites
- Node.js 18+
- Python 3.11+
- Access to the shared Exasol instance (host/port/user/password)
- A 2Factor.in API key (for phone OTP) and a Google OAuth Client ID (for Google Sign-In) — optional, only needed to test those specific features

## Setup

**1. Frontend**
```bash
npm install
cp .env.example .env.local   # fill in VITE_GOOGLE_CLIENT_ID
```

**2. Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env         # fill in EXASOL_*, JWT_SECRET_KEY, GOOGLE_CLIENT_ID, TWOFACTOR_API_KEY
```

## Run

**Backend** (from `backend/`):
```bash
uvicorn main:app --port 8000
```

**Frontend** (from the repo root, separate terminal):
```bash
npm run dev
```

Open **http://localhost:3000**. Backend API runs at **http://127.0.0.1:8000** (docs at `/docs`).

## Notes
- Sign up → Login work immediately. **Verify** (phone OTP) requires a real `TWOFACTOR_API_KEY` — it sends an actual SMS, so only test it when you mean to.
- Form-filling (search → answer questions → get PDF) requires a verified account.
