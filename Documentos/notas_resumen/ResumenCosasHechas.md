1. **Crear la estructura ordenada:**
   Creamos una jerarquia limpia de monorepo en la raiz (`TFG/`) separando el codigo (`Codigo/backend/`) de la documentacion (`Documentos/`) para mantener una organizacion profesional. 

2. **Crear un Entorno Virtual (venv) y servidor base:**
   Configuramos el entorno aislado en Python e instalamos FastAPI y Uvicorn, comprobando la documentacion automatica en `/docs`. 

3. **Configuracion del Control de Versiones y GitHub:**
   Inicializamos Git en la raiz del monorepo, configuramos `.gitignore`, ajustamos la identidad local del autor y sincronizamos el repositorio remoto en GitHub (`git push` / `git pull`). 

4. **Ingenieria del Software y Documentacion Completa:**
   * `DisenoSoftware.md`: Arquitectura de Monolito Modular, flujo hibrido, base de conocimiento desacoplada (`rules/`) y contrato JSON de salida. 
   * `Requisitos.md`: Especificacion IEEE 830 (`RF-01` a `RF-11` y `RNF-01` a `RNF-12`) con Python y C como lenguajes iniciales y actualizacion dinamica de reglas. 
   * `CasosDeUso.md`: Actores y casos de uso (`UC-01` a `UC-09`). 
   * `ModeladoSistema.md` y `PatronesDiseno.md`: Modelado estructural/comportamiento y catalogo de patrones aplicados (incluyendo Strategy por lenguaje y Externalized Knowledge Base). 
   * `ModeloDatos.md` y `EspecificacionesSeguridad.md`: Diseno de base de datos (`SCANS` con `rules_version`, `VULNERABILITIES`, `AUDIT_LOGS`) y controles de ciberseguridad. 
   * `PlanPruebas.md`: Estrategia de aseguramiento de la calidad (QA) con `pytest` y matriz de casos de prueba unitarios, de integracion y seguridad. 
   * Diagramas (`Documentos/diagramas/<nombre>/`): 5 subcarpetas independientes (`casos_uso`, `arquitectura_componentes`, `diagrama_clases`, `secuencia_analisis`, `modelo_datos`), cada una con su codigo `.puml` y su imagen `.svg` generada. 

5. **Documento Maestro de Contexto y Reglas (`ContextoIA.md`) en local:**
   Creamos el archivo de persistencia de reglas, prohibiciones, decisiones arquitectonicas y estado del proyecto, y lo excluimos en `.gitignore` para mantenerlo estrictamente privado en local sin subirlo a GitHub. 

6. **Creacion del Esqueleto Fisico Completo del Backend (`Codigo/backend/app/`):**
   Generamos toda la estructura fisica de directorios, paquetes (`__init__.py`) y archivos base del Monolito Modular, incluyendo la carpeta `app/modules/analyzer/rules/` (`loader.py`, `metadata.json`, `python_rules.json`, `c_rules.json`).

7. **Instalacion de Dependencias y Configuracion Centralizada (`requirements.txt`, `.env` y `app/core/config.py`):**
   * Habilitamos la politica de ejecucion de scripts en PowerShell para activar `venv` e instalamos `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `sqlmodel`, `pytest` y `httpx`.
   * Creamos `.env` con las variables de entorno locales y `app/core/config.py` aplicando el Patron Singleton (`@lru_cache()`) con Pydantic `BaseSettings`, verificado con exito en terminal.
