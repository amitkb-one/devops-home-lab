from fastapi import FastAPI
import os
import platform
import socket

app = FastAPI(title="DevOps Home Lab API", version="1.0.0")

@app.get("/")
def home():
    return {
        "message": "Welcome to my DevOps Home Lab",
        "environment": os.getenv("APP_ENV", "development"),
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "UP"}

@app.get("/system")
def system_info():
    return {
        "hostname": socket.gethostname(),
        "architecture": platform.machine(),
        "operating_system": platform.system()
    }
