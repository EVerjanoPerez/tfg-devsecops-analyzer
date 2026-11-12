1. **Crear la estructura ordenada:**
   Creamos una jerarquía limpia de monorepo en la raíz (`TFG/`) separando el código (`Codigo/backend/`) de la documentación (`Documentos/`) para mantener una organización profesional.

2. **Crear un Entorno Virtual (venv):**
   Usamos Python para crear una carpeta aislada `venv` dentro de backend, evitando conflictos de versiones en el sistema.

3. **Instalar las herramientas de servidor (FastAPI y Uvicorn):**
   Descargamos FastAPI (framework web) y Uvicorn (motor del servidor físico local).

4. **Crear el archivo main.py:**
   Escribimos el primer endpoint raíz de prueba y comprobamos el funcionamiento de la documentación automática en `http://127.0.0.1:8000/docs`.

5. **Configuración del Control de Versiones (Monorepo con Git):**
   * Inicializamos Git en la carpeta raíz (`TFG/`) para controlar conjuntamente el código y los documentos.
   * Creamos un archivo `.gitignore` general para proteger los entornos virtuales (`venv/`) y archivos temporales (`__pycache__/`).
   * Realizamos el primer commit oficial (`feat: estructura inicial...`).

6. **Sincronización con GitHub:**
   * Creamos el repositorio remoto en GitHub.
   * Configuramos la identidad local de Git (`user.name` y `user.email`) para asegurar la autoría correcta en equipos compartidos.
   * Realizamos el `git push` con éxito para respaldar el proyecto en la nube.
