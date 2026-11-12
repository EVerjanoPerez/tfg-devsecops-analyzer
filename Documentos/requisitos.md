# Especificación de Requisitos de Software (SRS)
**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG)  
**Versión:** 1.0  
**Estándar de referencia:** IEEE 830 / ISO 29148  

---

## 1. Requisitos Funcionales (RF)
*Definen qué debe hacer el sistema, sus servicios y comportamientos ante entradas específicas.*

### Módulo de Ingestión y Análisis SAST
* **RF-01 (Soporte Multi-lenguaje Extensible):** El sistema debe ser agnóstico al lenguaje en su capa de ingestión, comenzando con soporte completo de análisis híbrido (estático + IA) para **Python y C**, y dejando el motor de IA abierto a cualquier lenguaje estándar de programación mediante una arquitectura fácilmente ampliable.
* **RF-02 (Análisis Estático Híbrido):** El sistema debe ejecutar primero un motor de análisis estático sintáctico/AST rápido y determinista específico para el lenguaje recibido, delegando en motores de Inteligencia Artificial para análisis contextual profundo o detección de patrones complejos.
* **RF-03 (Detección y Localización de Vulnerabilidades):** El sistema debe identificar fallos de seguridad en el código analizado (como inyecciones o deserialización insegura en Python, o *buffer overflows* y gestión insegura de memoria en C) e indicar la ubicación exacta (archivo y número de línea) donde se produce cada hallazgo.
* **RF-04 (Clasificación Normativa de Seguridad):** Cada vulnerabilidad detectada debe clasificarse automáticamente asignándole su nivel de severidad (Crítico, Alto, Medio, Bajo), su categoría según **OWASP Top 10** y su identificador estándar **CWE** (*Common Weakness Enumeration*).
* **RF-05 (Generación de Remediaciones y Parches):** El sistema debe proporcionar para cada fallo detectado una explicación técnica de por qué ocurre la vulnerabilidad y una propuesta de solución con un ejemplo práctico de código corregido.

### Módulo de Persistencia, Caché e Historial
* **RF-06 (Caché Inteligente por Huella Digital):** El sistema debe calcular el hash criptográfico (SHA-256) del código recibido; si idéntico código ya fue analizado previamente, devolverá el resultado almacenado sin reprocesar los motores.
* **RF-07 (Almacenamiento de Histórico):** El sistema debe persistir en base de datos los metadatos y resultados de cada escaneo realizado para su posterior consulta o auditoría.
* **RF-08 (Exportación de Informes):** El sistema debe permitir consultar los análisis históricos en formato estructurado JSON (dejando preparada la arquitectura para futura exportación a reportes legibles como PDF/Markdown).

### Escalabilidad Funcional (Fases Futuras Previstas en Arquitectura)
* **RF-09 (Análisis de Proyectos Completos):** El sistema debe estar preparado para recibir archivos comprimidos (`.zip`) o URLs de repositorios Git, descomprimirlos de forma segura y escanear recursivamente múltiples archivos.
* **RF-10 (Ejecución Dinámica Aislada - Sandbox):** El sistema contemplará a futuro la ejecución controlada del código analizado dentro de contenedores efímeros aislados (Docker) para detectar vulnerabilidades en tiempo de ejecución sin comprometer el servidor anfitrión.

---

## 2. Requisitos No Funcionales (RNF)
*Definen los criterios de calidad, rendimiento, seguridad, arquitectura y restricciones bajo los cuales debe operar el sistema.*

### Arquitectura y Mantenibilidad
* **RNF-01 (Modularidad y Bajo Acoplamiento):** El backend debe seguir una arquitectura de Monolito Modular por dominios (`core`, `modules`, `common`), garantizando que la modificación o sustitución de un componente no afecte al funcionamiento del resto.
* **RNF-02 (Extensibilidad de Motores y Lenguajes):** Los motores de análisis deben implementar el patrón de diseño *Strategy* mediante una interfaz común (`BaseEngine`) y un registro dinámico por lenguaje, permitiendo añadir nuevos lenguajes o motores (AST, IA local, APIs externas) sin alterar la lógica central ni los contratos de la API.
* **RNF-03 (Independencia de Cliente):** El sistema debe exponer una API REST agnóstica basada en JSON, permitiendo que pueda ser consumida indistintamente por interfaces web (como Angular), aplicaciones móviles, extensiones de IDE o herramientas CLI.

### Seguridad y Resiliencia
* **RNF-04 (Cero Ejecución Insegura):** En su fase estática, el servidor nunca debe compilar ni ejecutar el código fuente proporcionado por el usuario, tratándolo estrictamente como datos/texto o árboles sintácticos abstractos.
* **RNF-05 (Aislamiento de Fallos / Tolerancia):** Los errores producidos en un motor de análisis o en la validación de un archivo deben ser capturados mediante control de excepciones a nivel de módulo sin provocar la caída del servidor principal.
* **RNF-06 (Validación Estricta y Protección DoS):** Todas las entradas HTTP deben validarse mediante esquemas estrictos (Pydantic) con límites de tamaño de carga útil y limitación de tasa (*Rate Limiting*).
* **RNF-07 (Trazabilidad y Auditoría):** El sistema debe contar con un mecanismo centralizado de registro de eventos (*logging*) que almacene fecha, hora, módulo y traza de errores para diagnóstico rápido.
* **RNF-08 (Transparencia y Control de Dependencias):** Todas las dependencias externas deben estar auditadas y fijadas en `requirements.txt`, evitando librerías no verificadas o puertas traseras, y gestionando credenciales mediante variables de entorno (`.env`).

### Rendimiento y Eficiencia de Costes
* **RNF-09 (Procesamiento Asíncrono):** La API debe operar de forma asíncrona (FastAPI/Uvicorn) para gestionar peticiones concurrentes sin bloqueos, dejando prevista la integración de colas de tareas en segundo plano para análisis pesados.
* **RNF-10 (Optimización Computacional y Económica):** El flujo de análisis debe minimizar el consumo de recursos y costes de APIs externas priorizando reglas estáticas locales rápidas y el uso de caché antes de invocar modelos de IA.

### Calidad y Ciclo de Vida
* **RNF-11 (Integración Continua - CI/CD):** El repositorio debe integrar flujos automatizados (GitHub Actions) que ejecuten pruebas unitarias (`pytest`) y validaciones de sintaxis ante cada actualización del código.
