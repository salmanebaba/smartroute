from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(title="Smart Bin Route Optimizer")

app.include_router(router)



# Autoriser toutes les origines (pour dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tu peux mettre ["https://modern-kitten-basically.ngrok-free.app"] pour plus de sécurité
    allow_credentials=True,
    allow_methods=["POST"],  # ou ["POST", "GET"]
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
