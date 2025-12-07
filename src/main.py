from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.api import dte_router, producto_router, cliente_router
from src.core.db import Base, engine
import logging
import os

logging.basicConfig(level=logging.INFO)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Emisión de DTE",
    description="API para gestionar la emisión de Documentos Tributarios Electrónicos (DTE) en El Salvador.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, reemplazar con dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the frontend directory to serve static assets (css, js)
# We mount it at /static so in HTML we use /static/css/styles.css
app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(dte_router.router, prefix="/api")
app.include_router(producto_router.router, prefix="/api")
app.include_router(cliente_router.router, prefix="/api")

@app.get("/")
def read_root():
    return FileResponse('frontend/index.html')

@app.get("/emitir")
def read_emitir():
    return FileResponse('frontend/emitir.html')

@app.get("/invalidar")
def read_invalidar():
    return FileResponse('frontend/invalidar.html')

@app.get("/productos")
def read_productos():
    return FileResponse('frontend/productos.html')

@app.get("/reportes")
def read_reportes():
    return FileResponse('frontend/reportes.html')

@app.get("/compras")
def read_compras():
    return FileResponse('frontend/compras.html')

@app.get("/ventas")
def read_ventas():
    return FileResponse('frontend/ventas.html')

@app.get("/lotes")
def read_lotes():
    return FileResponse('frontend/lotes.html')

@app.get("/pos")
def read_pos():
    return FileResponse('frontend/pos.html')

@app.get("/clientes")
def read_clientes():
    return FileResponse('frontend/clientes.html')
