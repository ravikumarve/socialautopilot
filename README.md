# Social Autopilot

> A fully automated social media promotion dashboard with human-in-the-loop review.
> Generates, queues, and publishes content across Twitter/X, LinkedIn, and Threads.

![Social Autopilot Dashboard](https://via.placeholder.com/800x400?text=Social+Autopilot+Dashboard)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Development](#development)
- [AI Service Pattern](#ai-service-pattern)
- [Review Queue Contract](#review-queue-contract)
- [What Not to Do](#what-not-to-do)
- [Contributing](#contributing)
- [License](#license)

## Overview

Social Autopilot is a local-first, CPU-only application designed for solo builders who want to automate their social media promotion while maintaining control through a human-in-the-loop review process.

**Current Status**: Active development - upgrading AI backbone from Claude API to Gemini 2.5 Pro, adding trend awareness, bulk generation, and analytics feedback loop.

## Features

- 🤖 **AI-Powered Content Generation**: Creates engaging posts for Twitter/X, LinkedIn, and Threads
- 👀 **Human-in-the-Loop Review**: Every post goes through approval/edit/reject before publishing
- ⏰ **Scheduled Publishing**: Approved posts are queued and published automatically
- 📈 **Trend Awareness** (Planned): Incorporates trending topics using Gemini's grounding feature
- 📦 **Bulk Generation** (Planned): Generate weeks of content in one go using Gemini's 1M token context
- 📊 **Analytics & Feedback** (Planned): Track post performance and get AI-powered insights
- 🔒 **Privacy-Focused**: 100% local processing, no cloud dependencies for core functionality
- 💰 **Budget-Friendly**: Uses free tiers and local tools wherever possible

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | Next.js 13+ (App Router), React     |
| Backend     | FastAPI (Python)                    |
| Database    | SQLite via SQLAlchemy               |
| AI (Current)| Claude API (Anthropic)              |
| AI (Target) | Gemini 2.5 Pro (Google)             |
| Distribution| Gumroad / LemonSqueezy              |
| Deployment  | Local-first, CPU-only (Linux Mint)  |

## Project Structure

```
social-autopilot/
├── frontend/                 # Next.js app
│   ├── app/                  # App router pages
│   │   ├── layout.tsx        # Root layout
│   │   └── page.tsx          # Dashboard page
│   ├── components/           # Reusable UI components
│   │   ├── AnalyticsPanel.tsx
│   │   ├── BulkGenerateButton.tsx
│   │   └── ReviewQueue.tsx
│   ├── lib/                  # Utilities, API clients
│   │   └── api.ts            # Backend API client
│   ├── globals.css           # Tailwind CSS styles
│   ├── package.json          # Frontend dependencies
│   └── tsconfig.json         # TypeScript configuration
├── backend/                  # FastAPI app
│   ├── main.py               # Entry point
│   ├── db.py                 # Database session and initialization
│   ├── models.py             # SQLAlchemy models
│   ├── requirements.txt      # Python dependencies
│   ├── routers/              # Route handlers
│   │   ├── analytics.py      # Analytics endpoints
│   │   ├── generate.py       # Bulk generation endpoints
│   │   ├── posts.py          # Post CRUD operations
│   │   └── review.py         # Review queue endpoints
│   └── services/             # Business logic
│       └── ai_service.py     # AI service (Gemini 2.5 Pro)
├── .env.example              # Environment variables template
├── AGENTS.md                 # Agent context (this file)
└── Makefile                  # Development commands
```

## Getting Started

### Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- pip (Python package manager)
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd social-autopilot
   ```

2. Install dependencies:
   ```bash
   make install-deps
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys:
   #   GEMINI_API_KEY=your_key_here
   #   TWITTER_BEARER_TOKEN=
   #   LINKEDIN_ACCESS_TOKEN=
   #   THREADS_ACCESS_TOKEN=
   #   DATABASE_URL=sqlite:///./social_autopilot.db
   ```

### Running the Application

```bash
# Start both backend and frontend services
make dev

# Or run them separately in different terminals:
# Terminal 1: Backend
make backend

# Terminal 2: Frontend
make frontend
```

- Backend API: http://localhost:8000
- Frontend Dashboard: http://localhost:3000

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# AI API Keys
GEMINI_API_KEY=your_key_here

# Social Media API Keys (obtain from respective platforms)
TWITTER_BEARER_TOKEN=
LINKEDIN_ACCESS_TOKEN=
THREADS_ACCESS_TOKEN=

# Database
DATABASE_URL=sqlite:///./social_autopilot.db
```

## Development

### Backend

```bash
# Install backend dependencies
cd backend && pip install -r requirements.txt

# Run the backend server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
# Install frontend dependencies
cd frontend && npm install

# Run the frontend development server
npm run dev
```

## AI Service Pattern

All AI interactions should follow this pattern in `backend/services/ai_service.py`:

```python
import google.generativeai as genai
import os
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

async def generate_post(platform: str, topic: str, brand_voice: str) -> str:
    try:
        prompt = build_prompt(platform, topic, brand_voice)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        return fallback_post(platform, topic)
```

## Review Queue Contract

This is the core UX guarantee - **never bypass it**:

1. AI generates draft → saved to `posts` table with `status = "draft"`
2. User sees draft in review dashboard → approves, edits, or rejects
3. On approve → `status = "queued"`, scheduler picks it up and publishes
4. On reject → `status = "rejected"`, logged for analytics

**Any new feature that generates content must write to the draft queue first.**

## What Not to Do

- ❌ Do NOT add Redis, Celery, or any heavy queue system — use APScheduler (already in stack)
- ❌ Do NOT use Docker for local dev — run services directly
- ❌ Do NOT suggest cloud DB migrations — SQLite is intentional for local-first
- ❌ Do NOT add authentication/OAuth — this is a personal dashboard, not multi-tenant
- ❌ Do NOT use any paid third-party APIs without flagging the cost first
- ❌ Do NOT break the human-in-the-loop review step

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [AGENTS.md](AGENTS.md) for detailed development guidelines and conventions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ for solo builders and indie hackers
- Inspired by the need for authentic, automated social media presence
- Powered by Google's Gemini 2.5 Pro AI model