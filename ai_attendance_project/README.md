# AI Attendance + AI Tutor (Django)

Features:
- Student register with face image
- One-click webcam attendance (face_recognition)
- Attendance report (per user; admin sees all)
- AI Tutor chat (OpenAI) with graceful offline fallback

## Quickstart
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
# (Optional) set your OpenAI API key to use AI Tutor
set OPENAI_API_KEY=sk-...   # PowerShell: $env:OPENAI_API_KEY="sk-..."
python manage.py runserver
```

Open:
- Home:       http://127.0.0.1:8000/
- Register:   http://127.0.0.1:8000/register/
- Login:      http://127.0.0.1:8000/login/
- Mark:       http://127.0.0.1:8000/mark/
- Report:     http://127.0.0.1:8000/report/
- AI Tutor:   http://127.0.0.1:8000/tutor/chat/

## Notes
- The `face_recognition` package requires `dlib`. On Windows, prefer installing prebuilt wheels.
- Webcam access must be allowed by your OS.
- In production, move static files with `python manage.py collectstatic` and set proper `DEBUG=False` and `ALLOWED_HOSTS`.
