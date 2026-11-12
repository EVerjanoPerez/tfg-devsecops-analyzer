from fastapi import FastAPI

# Inicializamos la aplicación de FastAPI
app = FastAPI(
    title="TFG DevSecOps Analyzer",
    version="1.0.0"
)

# Ruta raíz de prueba (endpoint GET)
@app.get("/")
def read_root():
    return {
        "estado": "activo",
        "mensaje": "¡Bienvenido al backend de tu TFG de ciberseguridad con IA!"
    }