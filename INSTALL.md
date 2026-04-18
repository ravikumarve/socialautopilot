# INSTALL.md

## 🛠️ Installation Guide for Social Autopilot

This document provides detailed instructions for setting up **Social Autopilot** on different environments. The project is designed to run locally on CPU-only hardware (Linux Mint preferred).

## 🧰 System Requirements

| Component        | Minimum Requirement          |
|------------------|------------------------------|
| OS               | Linux Mint (20+) or Ubuntu    |
| CPU              | 4 cores (Intel i5 or equivalent) |
| RAM              | 8GB+                          |
| Disk Space       | 5GB (plus space for SQLite DB) |
| Python           | 3.9+                           |
| Node.js          | 16.x+                          |

> **Note**: This project avoids GPU dependencies. No CUDA or TensorFlow requirements.

## 📦 Dependency Installation

### Backend (Python)
```bash
# Install Python dependencies
 cd backend
 pip install -r requirements.txt

# Required packages include:
# - fastapi
# - uvicorn
# - sqlalchemy
# - python-dotenv
# - google-genai (for Gemini API)
```

### Frontend (Next.js)
```bash
# Install Node.js dependencies
 cd frontend
 npm install

# Required packages include:
# - next
# - react
# - react-dom
# - tailwindcss
# - axios
```

## 🔧 Configuration

### 1. Environment Variables
Create `.env` in the project root:
```bash
GEMINI_API_KEY=your_gemini_key_here
TWITTER_BEARER_TOKEN=your_twitter_token
LINKEDIN_ACCESS_TOKEN=your_linkedIn_token
THREADS_ACCESS_TOKEN=your_threads_token
DATABASE_URL=sqlite:///./social_autopilot.db
```

### 2. Database Setup
```bash
# Initialize SQLite database
 cd backend
 python -c "from backend.db import init_db; init_db()"
```

## 🚀 Running the Application

### Development Mode
```bash
# Backend (from root)
 cd backend
 uvicorn main:app --reload --port 8000

# Frontend (in new terminal)
 cd frontend
 npm run dev
```

### Production Build (Linux)
```bash
# Build frontend
 cd frontend
 npm run build

# Run backend in production
 cd backend
 uvicorn main:app --port 8000 --workers 4
```

## 🧪 Testing the Setup

### Backend Test
```bash
 curl http://localhost:8000/docs
# Should return Swagger UI for FastAPI endpoints
```

### Frontend Test
```bash
# Open in browser
 http://localhost:3000
# Should show Social Autopilot dashboard
```

## 🛠️ Troubleshooting

### Common Issues
| Symptom | Solution |
|---------|----------|
| **API Key Errors** | Verify `.env` exists and has correct keys |
| **Database Errors** | Run `python -c "from backend.db import init_db; init_db()"` |
| **Port Conflicts** | Use `--port` flag with uvicorn to change port |
| **Missing Dependencies** | Re-run `pip install -r requirements.txt` and `npm install` |

### Logs
- Backend logs: `backend/logs/` directory
- Frontend logs: Browser console and `npm run dev` output

## 📚 Alternative Setups

### Docker (Not Recommended)
While the project supports local-first development, Docker can be used for deployment:
```bash
# Build image
 docker build -t social-autopilot .

# Run container
 docker run -p 8000:8000 -v ~/.social-autopilot:/app/data social-autopilot
```
> **Note**: Docker is not required for development and may violate local-first principles.

## 🧩 Third-Party Services

| Service | Purpose | Free Tier |
|--------|---------|-----------|
| Gemini API | Content generation | $5/month free |
| Twitter API | Posting | Free tier available |
| LinkedIn API | Posting | Requires approval |
| Threads API | Posting | Free |

> All third-party services must be configured via `.env` variables.

## 📞 Support

For setup issues, check:
1. [README.md](README.md)
2. [CONTRIBUTING.md](CONTRIBUTING.md)
3. GitHub Issues (after searching existing problems)

---

> **Important**: Always prefer local execution. Cloud deployment may violate the project's local-first design principles.