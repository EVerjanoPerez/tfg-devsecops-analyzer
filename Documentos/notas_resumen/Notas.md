**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG)[cite: 12]

**Stack Tecnologico:** Python, FastAPI, Uvicorn, Pydantic, pydantic-settings, SQLAlchemy/SQLModel, Pytest, httpx, Git, GitHub, GitHub Actions (CI/CD).[cite: 12]

**Lenguajes soportados inicialmente (MVP):** Python y C (arquitectura extensible mediante Patron Strategy y `EngineRegistry` para anadir mas lenguajes sin tocar el core).[cite: 12]

**Comandos clave del entorno (en PowerShell dentro de `Codigo/backend`):**
* Habilitar scripts locales (si PowerShell bloquea `venv`): `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
* Activar entorno virtual: `.\venv\Scripts\Activate.ps1`[cite: 12]
* Instalar dependencias desde archivo: `python -m pip install -r requirements.txt`
* Encender el servidor de desarrollo: `uvicorn app.main:app --reload`[cite: 12]
* Direccion local del servidor: `http://127.0.0.1:8000`[cite: 12]
* Documentacion automatica interactiva: `http://127.0.0.1:8000/docs`[cite: 12]

**Comandos clave de Git y GitHub (en la raiz `TFG/`):**
* Configurar autor local: `git config user.name "Tu Nombre"` y `git config user.email "tu-correo"`[cite: 12]
* Traer cambios de la nube antes de trabajar: `git pull origin main`[cite: 12]
* Ver estado de archivos: `git status`[cite: 12]
* Anadir cambios al radar: `git add .`[cite: 12]
* Guardar commit: `git commit -m "mensaje descriptivo"`[cite: 12]
* Subir cambios a la nube: `git push -u origin main` (o simplemente `git push` tras la primera subida)[cite: 12]
* Sacar un archivo del radar de Git sin borrarlo del disco: `git rm --cached ruta/del/archivo`[cite: 12]

**Principios de Arquitectura, Seguridad, Estilo y Trazabilidad:**
* Monolito modular (`core/`, `modules/`, `common/`).[cite: 12]
* Patron Strategy (`BaseEngine`) + `EngineRegistry` para desacoplar motores estaticos por lenguaje (`PythonASTEngine`, `CStaticEngine`, y futuros lenguajes) y `AIEngine`.[cite: 12]
* **Base de Conocimiento Desacoplada (`rules/`):** Reglas de deteccion, mapeos OWASP/CWE y plantillas de solucion almacenadas en JSON externos versionados (`metadata.json`, `python_rules.json`, `c_rules.json`) para actualizar estandares sin tocar el codigo.[cite: 12]
* Clasificacion normativa obligatoria: Severidad + OWASP Top 10 + CWE + Propuesta de solucion/parcheo.[cite: 12]
* Cache por `(code_hash SHA-256, rules_version)` para invalidar resultados si se actualizan las reglas.[cite: 12]
* Nunca ejecutar codigo no confiable en el servidor (solo analisis estatico; ejecucion futura aislada en contenedores Docker).[cite: 12]
* **Estilo de codigo obligatorio:** Todo el codigo fuente debe estar exhaustivamente comentado linea por linea y funcion por funcion para que cualquier persona sin experiencia previa pueda comprenderlo.
* **Regla de oro:** Cualquier cambio en codigo que altere lo documentado requiere aviso previo y actualizacion sincronizada de `.md`, `.puml`/`.svg` y `ContextoIA.md`, manteniendo siempre los nombres exactos de los archivos y sin emojis.[cite: 12]
* **Archivo local privado:** `Documentos/ContextoIA.md` esta excluido en `.gitignore` y **nunca** debe subirse a GitHub.[cite: 12]