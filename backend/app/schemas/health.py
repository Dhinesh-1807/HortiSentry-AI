from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str = "ok"
    database: str = "connected"
    ml_mode: str = "DEMO"
    app_name: str
    environment: str
