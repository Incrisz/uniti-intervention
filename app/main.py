from fastapi import FastAPI
from app.routers import intervention, message, health

app = FastAPI(
  title="Uniti AI API",
  description="API for Intervention Engine (Model 1) and Message Optimizer (Model 2)",
  version="1.0.0",
)

# Include routers
app.include_router(intervention.router)
app.include_router(message.router)
app.include_router(health.router)
