**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG) 

**Stack Tecnológico:** Python, FastAPI, Uvicorn, Pydantic, SQLAlchemy/SQLModel, Git, GitHub, GitHub Actions (CI/CD).

**Lenguajes soportados inicialmente (MVP):** Python y C (arquitectura extensible mediante Patrón Strategy para añadir más lenguajes sin tocar el core).

**Comandos clave del entorno:**
* Activar entorno virtual (en PowerShell): `.\venv\Scripts\Activate.ps1`  
* Encender el servidor de desarrollo: `uvicorn app.main:app --reload`  
* Dirección local del servidor: `http://127.0.0.1:8000`  
* Documentación automática interactiva: `http://127.0.0.1:8000/docs`

**Comandos clave de Git y GitHub:**
* Configurar autor local: `git config user.name "Tu Nombre"` y `git config user.email "tu-correo"`
* Inicializar repositorio local (en raíz): `git init`
* Traer cambios de la nube antes de trabajar: `git pull origin main`
* Ver estado de archivos: `git status`
* Añadir cambios al radar: `git add .`
* Guardar commit: `git commit -m "mensaje descriptivo"`
* Subir cambios a la nube: `git push -u origin main`

**Principios de Arquitectura y Seguridad:**
* Monolito modular (`core/`, `modules/`, `common/`).
* Patrón Strategy (`BaseEngine`) + Registro dinámico de lenguajes para desacoplar motores estáticos (AST/patrones) y motores de IA.
* Clasificación normativa obligatoria: Severidad + OWASP Top 10 + CWE + Propuesta de solución/parcheo.
* Caché por hash SHA-256 para evitar re-análisis costosos.
* Nunca ejecutar código no confiable en el servidor (solo análisis estático; ejecución futura aislada en contenedores Docker).