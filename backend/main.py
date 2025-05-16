from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router

app = FastAPI(title="Smart Bin Route Optimizer")

app.include_router(router)



# Autoriser toutes les origines (pour dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["POST"], 
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run()
