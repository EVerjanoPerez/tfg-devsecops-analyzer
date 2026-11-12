1. **Crear la estructura ordenada:**
   Creamos una jerarquía limpia de monorepo en la raíz (`TFG/`) separando el código (`Codigo/backend/`) de la documentación (`Documentos/`) para mantener una organización profesional.

2. **Crear un Entorno Virtual (venv) y servidor base:**
   Configuramos el entorno aislado en Python e instalamos FastAPI y Uvicorn, comprobando la documentación automática en `/docs`.

3. **Configuración del Control de Versiones y GitHub:**
   Inicializamos Git en la raíz del monorepo, configuramos `.gitignore`, ajustamos la identidad local del autor y sincronizamos el repositorio remoto en GitHub (`git push` / `git pull`).

4. **Ingeniería del Software y Documentación Completa:**
   * `DisenoSoftware.md`: Arquitectura de Monolito Modular, flujo híbrido y contrato JSON de salida.
   * `Requisitos.md`: Especificación IEEE 830 (`RF-01` a `RF-10` y `RNF-01` a `RNF-11`) con Python y C como lenguajes iniciales.
   * `CasosDeUso.md`: Actores y casos de uso (`UC-01` a `UC-09`).
   * `ModeladoSistema.md` y `PatronesDiseno.md`: Modelado estructural/comportamiento y catálogo de patrones aplicados.
   * `ModeloDatos.md` y `EspecificacionesSeguridad.md`: Diseño de base de datos (`SCANS`, `VULNERABILITIES`, `AUDIT_LOGS`) y controles de ciberseguridad.
   * Diagramas (`Documentos/diagramas/<nombre>/`): 5 subcarpetas independientes (`casos_uso`, `arquitectura_componentes`, `diagrama_clases`, `secuencia_analisis`, `modelo_datos`), cada una con su código `.puml` y su imagen `.svg` generada.

5. **Documento Maestro de Contexto y Reglas (`ContextoIA.md`) en local:**
   Creamos el archivo de persistencia de reglas, prohibiciones, decisiones arquitectónicas y estado del proyecto, y lo excluimos en `.gitignore` para mantenerlo estrictamente privado en local sin subirlo a GitHub.