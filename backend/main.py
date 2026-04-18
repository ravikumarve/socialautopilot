from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.routers import posts, review, analytics, generate

app = FastAPI(title="Social Autopilot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(review.router, prefix="/review", tags=["review"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(generate.router, prefix="/generate", tags=["generate"])


@app.get("/")
async def root():
    return {"message": "Social Autopilot API is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
