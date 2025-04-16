from fastapi import FastAPI
from app.drive.routes.profile_routes import router as profile_router
from app.drive.routes.product_routes import router as product_router
from app.drive.routes.subproduct_routes import router as subproduct_router

app = FastAPI(title="Inventory Drive Storage API")

@app.get("/")
async def root():
    return {"message": "🚀 API de almacenamiento de archivos con Google Drive"}

# Routers ya incluyen su propio prefix
app.include_router(profile_router)
app.include_router(product_router)
app.include_router(subproduct_router)
