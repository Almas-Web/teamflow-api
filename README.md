# 🚀 TeamFlow API

TeamFlow API is a high-performance, enterprise-grade backend system engineered for professional project management and team collaboration. The project follows a clean architecture and integrates modern backend technologies, DevOps practices, caching, asynchronous processing, monitoring, and security to deliver a scalable and production-ready API.

---

# 🏗️ Architecture

```
                Client
                   │
                   ▼
        Nginx (Reverse Proxy)
                   │
                   ▼
        Gunicorn + Uvicorn
                   │
                   ▼
               FastAPI API
          ┌────────┴────────┐
          ▼                 ▼
    PostgreSQL          Redis Cache
          │                 │
          └──────┬──────────┘
                 ▼
              Celery Worker
                 │
                 ▼
       Email / Background Tasks
```

---

# 🛠 Tech Stack

## Backend

- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Alembic
- Pydantic
- JWT Authentication
- Redis
- Celery

## DevOps

- Docker
- GitHub Actions (CI/CD)
- Nginx
- Gunicorn
- Uvicorn
- Ubuntu VPS
- Render

## Monitoring

- Prometheus
- Grafana

## Security

- JWT Authentication
- Rate Limiting
- Secure Headers
- CORS
- HTTPS / SSL
- Password Hashing

---

# ⚡ Features

- User Authentication
- Workspace Management
- Project Management
- Task Management
- Task Comments
- Team Member Management
- Role-Based Permissions
- Dashboard API
- Redis Caching
- Background Email Processing
- Multi-Provider Email Support
- Centralized Logging
- RESTful API
- Database Indexing
- Eager Loading Optimization
- Production Ready Deployment

---

# 📂 Project Structure

```
TEAMFLOW-API/
│
├── apis/                  # API Routes
├── core/                  # Configurations & Exception Handlers
├── db/
│   ├── models/            # SQLAlchemy Models
│   ├── session.py
│   └── base.py
│
├── repositories/          # Database Layer
├── schemas/               # Pydantic Schemas
├── tasks/                 # Celery Tasks
├── utils/                 # Helper Utilities
├── tests/                 # Pytest Tests
│
├── alembic/
├── main.py
├── worker.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

# 📦 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Almas-Web/teamflow-api.git
cd teamflow-api
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
DATABASE_URL=
REDIS_URL=

SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

AWS_ACCESS_KEY=
AWS_SECRET_KEY=

BREVO_API_KEY=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_USERNAME=
EMAIL_PASSWORD=
```

---

## 5. Run Database Migrations

```bash
alembic upgrade head
```

---

## 6. Start Redis

```bash
redis-server
```

---

## 7. Start Celery Worker

```bash
celery -A worker.celery worker --loglevel=info
```

---

## 8. Run FastAPI

Development

```bash
uvicorn main:app --reload
```

Production

```bash
gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    --workers 4
```

---

# 🧪 Running Tests

```bash
pytest -v
```

Generate Coverage Report

```bash
pytest --cov=. --cov-report=html
```

---

# 📊 Monitoring

Prometheus collects application metrics.

Grafana visualizes dashboards for:

- API Performance
- CPU Usage
- Memory Usage
- Redis Metrics
- PostgreSQL Metrics
- Request Rate
- Error Rate

---

# 🚀 Deployment

Supported deployment platforms:

- Render
- Ubuntu VPS
- Docker
- Nginx
- Gunicorn
- GitHub Actions CI/CD

---

# 🔒 Security

- JWT Authentication
- Password Hashing
- Role-Based Access Control
- Rate Limiting
- Secure Headers
- HTTPS
- CORS Protection

---

# 📝 Logging

Application logs are stored in:

```
logs/app.log
```

Logging includes:

- API Requests
- Errors
- Exceptions
- Authentication Logs
- Background Tasks

---

# 👨‍💻 Author

**Almas Hossen**

Python Backend Developer

GitHub:
https://github.com/Almas-Web


---

# ⭐ Future Improvements

- WebSocket Notifications
- File Upload (AWS S3)
- API Versioning
- Docker Compose Deployment
- Kubernetes Support
- OpenTelemetry
- Elasticsearch Logging
- RabbitMQ Support

---

## 📄 License

This project is licensed under the MIT License.

---

Built with ❤️ using FastAPI.