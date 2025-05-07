from fastapi import FastAPI
from api import router as api_router
from utils.database import init_db


app = FastAPI(title="Sales Analytics API")


app.include_router(api_router,prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 