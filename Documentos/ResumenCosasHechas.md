1. **Crear la estructura ordenada:**
   Creamos una jerarquía limpia de monorepo en la raíz (`TFG/`) separando el código (`Codigo/backend/`) de la documentación (`Documentos/`) para mantener una organización profesional.

2. **Crear un Entorno Virtual (venv) y servidor base:**
   Configuramos el entorno aislado en Python e instalamos FastAPI y Uvicorn, comprobando la documentación automática en `/docs`.

3. **Configuración del Control de Versiones y GitHub:**
   Inicializamos Git en la raíz del monorepo, configuramos `.gitignore`, ajustamos la identidad local del autor y sincronizamos el repositorio remoto en GitHub (`git push` / `git pull`).

4. **Análisis y Diseño de Arquitectura de Software (`DisenoSoftware.md`):**
   Definimos la arquitectura de Monolito Modular (`app/`, `core/`, `modules/`, `common/`), los patrones de diseño (*Strategy*, *Repository*, Inyección de Dependencias), el flujo de datos híbrido, el contrato JSON de vulnerabilidades (con mapeo OWASP Top 10, CWE y propuesta de parcheo) y las medidas de resiliencia y seguridad.

5. **Especificación de Requisitos de Software (`Requisitos.md`):**
   Documentamos formalmente los Requisitos Funcionales (RF-01 a RF-10) y No Funcionales (RNF-01 a RNF-11) bajo estándar IEEE 830, estableciendo **Python y C** como los lenguajes iniciales de análisis sobre una arquitectura fácilmente extensible a otros lenguajes.