from fastapi import FastAPI
from src.api import dte_router
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Sistema de Emisión de DTE",
    description="API para gestionar la emisión de Documentos Tributarios Electrónicos (DTE) en El Salvador.",
    version="1.0.0"
)

app.include_router(dte_router.router)

@app.get("/")
def read_root():
    return {"message": "DTE Emission System API is running."}
