from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from api_server.routes import strategies
from api_server.api_key import get_api_key

app = FastAPI(
    title="Strategy Monitor API",
    description="API for managing Market Maker Strategies",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()
router.include_router(strategies.router, dependencies=[Depends(get_api_key)])
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to MM Manager API"}
