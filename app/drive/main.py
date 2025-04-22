from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.drive.config import settings

from app.drive.routes.profile_routes import router as profile_router
from app.drive.routes.product_routes import router as product_router
from app.drive.routes.subproduct_routes import router as subproduct_router

app = FastAPI(title="Inventory Drive Storage API")

# Middleware CORS con lista de orígenes desde settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "🚀 API de almacenamiento de archivos con Google Drive"}

# Routers agrupados
app.include_router(profile_router)
app.include_router(product_router)
app.include_router(subproduct_router)
