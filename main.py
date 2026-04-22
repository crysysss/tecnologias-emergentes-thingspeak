from backend.main import app


if __name__ == "__main__":
    import uvicorn
    from backend.config import load_settings

    settings = load_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
