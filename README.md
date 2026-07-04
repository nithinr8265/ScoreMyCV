# ScoreMyCV — ATS Resume Analyzer

AI-powered ATS resume scoring platform. Built with Flask + Supabase + Groq AI.

---

## Quick Start

### 1. Clone and set up

```bash
cd scoremycv
python -m pip install -r requirements.txt
cp .env.example .env
# Fill in your keys in .env
```

### 2. Set up Supabase

1. Go to [supabase.com](https://supabase.com) → New Project
2. Open **SQL Editor** → paste and run `supabase_schema.sql`
3. Go to **Storage** → New Bucket → name it `resumes` → set to private
4. Copy your **Project URL** and **anon key** into `.env`

### 3. Get your Groq API key

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create an API key → paste into `.env` as `GROQ_API_KEY`

### 4. Set up Gmail SMTP (for password reset emails)

1. Google Account → Security → 2-Step Verification → App Passwords
2. Generate a password for "Mail" → paste into `.env` as `MAIL_PASSWORD`

### 5. Google OAuth (via Supabase)

1. Supabase Dashboard → Authentication → Providers → Google → Enable
2. Add your Google OAuth credentials (from Google Cloud Console)
3. Set redirect URL to: `https://yourdomain.com/auth/google/callback-page`

### 6. Run

```bash
python app.py
```

Visit `http://localhost:5000`

---

## Deploy to Render

1. Push to GitHub
2. Render → New Web Service → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT --timeout 120`
5. Add all environment variables from `.env`

---

## Project Structure

```
scoremycv/
├── app.py                    # Flask app, main routes
├── requirements.txt
├── Procfile                  # Render/Railway deployment
├── supabase_schema.sql       # Run in Supabase SQL Editor
├── .env.example
├── routes/
│   ├── auth.py               # Signup, login, Google OAuth, password reset
│   ├── resume.py             # File upload + text extraction
│   ├── analysis.py           # Groq AI analysis + history
│   ├── report.py             # PDF/DOCX report generation
│   └── admin.py              # Admin panel stats
├── utils/
│   ├── supabase_client.py    # Supabase connection
│   ├── groq_client.py        # Groq AI integration
│   ├── extractor.py          # PDF/DOCX text extraction
│   └── jwt_util.py           # JWT token helpers
├── templates/
│   ├── base.html             # Base layout
│   ├── landing.html          # Public landing page
│   ├── login.html / signup.html
│   ├── forgot_password.html / reset_password.html
│   ├── dashboard.html
│   ├── upload.html           # Resume upload + analysis trigger
│   ├── result.html           # Full ATS result with radar chart
│   ├── history.html          # Analysis history with search
│   ├── profile.html
│   ├── admin.html
│   └── partials/sidebar.html
└── static/
    ├── css/main.css          # Full design system, dark/light mode
    └── js/main.js            # Utilities, toasts, animations
```

---

## Make someone an admin

In Supabase SQL Editor:
```sql
UPDATE public.users SET role = 'admin' WHERE email = 'your@email.com';
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.0 |
| AI | Groq `llama-3.3-70b-versatile` |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth + bcrypt + JWT |
| File Storage | Supabase Storage |
| PDF extraction | pypdf |
| DOCX extraction | python-docx |
| Report generation | reportlab + python-docx |
| Frontend | HTML5, CSS3, Vanilla JS, Chart.js |
| Deployment | Render / Railway (Procfile included) |
