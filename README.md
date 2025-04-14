# SID_AI_RESEARCH_ASSISTANT
Use YouTube Data API v3 to fetch video titles, URLs, and IDs for a topic

---

## 📦 Libraries Used

- `Django`
- `djangorestframework`
- `django-cors-headers`
- `django-environ`
- `google-api-python-client`
- `youtube-transcript-api`

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Krishna-1350/SID_AI_RESEARCH_ASSISTANT.git

cd SID_AI_RESEARCH_ASSISTANT
```

### 2. Create Virtual Environment

```bash
python -m venv env
source env/bin/activate        # Linux/macOS
env\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Or manually if needed:

```bash
pip install Django
pip install djangorestframework
pip install django-cors-headers
pip install django-environ
pip install google-api-python-client
pip install youtube-transcript-api
pip install psycopg
pip install djangorestframework-simplejwt
pip install drf-yasg
```

### 📁 .env File
Create a .env file in the project root with the following content:

```bash
DATABASE_NAME='XXXXX'
DATABASE_USER='XXXXX'
DATABASE_PASS='XXXXX'
DATABASE_HOST='XXXXX'
DATABASE_PORT='XXXXX'
YOUTUBE_API_KEY='XXXXX'
```

### 🚀 Run the Server
```bash
python manage.py runserver 0.0.0.0:8000
```

Access API at:
```bash
http://localhost:8000/
```

## test 
