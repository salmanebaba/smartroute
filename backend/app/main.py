"""
Main FastAPI application for Smart Bin Route Optimizer.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.router import router
from app.config import APP_TITLE, CORS_ORIGINS

# Create FastAPI app
app = FastAPI(
    title=APP_TITLE,
    description="API for optimizing smart bin collection routes",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API information."""
    return {
        "service": APP_TITLE,
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
