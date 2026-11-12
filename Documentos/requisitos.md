# Especificacion de Requisitos de Software (SRS)

**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG)  
**Version:** 1.1  
**Estandar de referencia:** IEEE 830 / ISO 29148  

---

## 1. Requisitos Funcionales (RF)

*Definen que debe hacer el sistema, sus servicios y comportamientos ante entradas especificas.*

### Modulo de Ingestion y Analisis SAST
* **RF-01 (Soporte Multi-lenguaje Extensible):** El sistema debe ser agnostico al lenguaje en su capa de ingestion, comenzando con soporte completo de analisis hibrido (estatico + IA) para **Python y C**, y dejando el motor de IA abierto a cualquier lenguaje estandar de programacion mediante una arquitectura facilmente ampliable.
* **RF-02 (Analisis Estatico Hibrido):** El sistema debe ejecutar primero un motor de analisis estatico sintactico/AST rapido y determinista especifico para el lenguaje recibido, delegando en motores de Inteligencia Artificial para analisis contextual profundo o deteccion de patrones complejos.
* **RF-03 (Deteccion y Localizacion de Vulnerabilidades):** El sistema debe identificar fallos de seguridad en el codigo analizado (como inyecciones o deserializacion insegura en Python, o *buffer overflows* y gestion insegura de memoria en C) e indicar la ubicacion exacta (archivo y numero de linea) donde se produce cada hallazgo.
* **RF-04 (Clasificacion Normativa de Seguridad):** Cada vulnerabilidad detectada debe clasificarse automaticamente asignandole su nivel de severidad (Critico, Alto, Medio, Bajo), su categoria segun **OWASP Top 10** y su identificador estandar **CWE** (*Common Weakness Enumeration*).
* **RF-05 (Generacion de Remediaciones y Parches):** El sistema debe proporcionar para cada fallo detectado una explicacion tecnica de por que ocurre la vulnerabilidad y una propuesta de solucion con un ejemplo practico de codigo corregido.

### Modulo de Persistencia, Cache e Historial
* **RF-06 (Cache Inteligente por Huella Digital y Version de Reglas):** El sistema debe calcular el hash criptografico (SHA-256) del codigo recibido; si identico codigo ya fue analizado previamente bajo la misma version activa de reglas (`rules_version`), devolvera el resultado almacenado sin reprocesar los motores.
* **RF-07 (Almacenamiento de Historico):** El sistema debe persistir en base de datos los metadatos y resultados de cada escaneo realizado para su posterior consulta o auditoria.
* **RF-08 (Exportacion de Informes):** El sistema debe permitir consultar los analisis historicos en formato estructurado JSON (dejando preparada la arquitectura para futura exportacion a reportes legibles como PDF/Markdown).

### Escalabilidad Funcional y Base de Conocimiento
* **RF-09 (Analisis de Proyectos Completos):** El sistema debe estar preparado para recibir archivos comprimidos (`.zip`) o URLs de repositorios Git, descomprimirlos de forma segura y escanear recursivamente multiples archivos.
* **RF-10 (Ejecucion Dinamica Aislada - Sandbox):** El sistema contemplara a futuro la ejecucion controlada del codigo analizado dentro de contenedores efimeros aislados (Docker) para detectar vulnerabilidades en tiempo de ejecucion sin comprometer el servidor anfitrion.
* **RF-11 (Base de Conocimiento y Reglas Actualizables):** El sistema debe almacenar las definiciones de patrones de ataque, mapeos normativos (OWASP Top 10, CWE) y plantillas de remediacion en archivos externos estructurados (JSON/YAML) versionados, permitiendo actualizar o incorporar nuevas reglas sin modificar el codigo fuente de los motores ni reiniciar el nucleo.

---

## 2. Requisitos No Funcionales (RNF)

*Definen los criterios de calidad, rendimiento, seguridad, arquitectura y restricciones bajo los cuales debe operar el sistema.*

### Arquitectura y Mantenibilidad
* **RNF-01 (Modularidad y Bajo Acoplamiento):** El backend debe seguir una arquitectura de Monolito Modular por dominios (`core`, `modules`, `common`), garantizando que la modificacion o sustitucion de un componente no afecte al funcionamiento del resto.
* **RNF-02 (Extensibilidad de Motores y Lenguajes):** Los motores de analisis deben implementar el patron de diseno *Strategy* mediante una interfaz comun (`BaseEngine`) y un registro dinamico por lenguaje (`EngineRegistry`), permitiendo anadir nuevos lenguajes o motores (AST, IA local, APIs externas) sin alterar la logica central ni los contratos de la API.
* **RNF-03 (Independencia de Cliente):** El sistema debe exponer una API REST agnostica basada en JSON, permitiendo que pueda ser consumida indistintamente por interfaces web (como Angular), aplicaciones moviles, extensiones de IDE o herramientas CLI.
* **RNF-12 (Desacoplamiento de Conocimiento y Versionado de Cache):** Los motores estaticos deben cargar dinamicamente sus reglas desde una base de conocimiento externa (`rules/`), asociando cada escaneo en cache a la version de reglas vigente (`rules_version`) para invalidar automaticamente resultados obsoletos cuando se actualicen las definiciones de seguridad.

### Seguridad y Resiliencia
* **RNF-04 (Cero Ejecucion Insegura):** En su fase estatica, el servidor nunca debe compilar ni ejecutar el codigo fuente proporcionado por el usuario, tratandolo estrictamente como datos/texto o arboles sintacticos abstractos.
* **RNF-05 (Aislamiento de Fallos / Tolerancia):** Los errores producidos en un motor de analisis o en la validacion de un archivo deben ser capturados mediante control de excepciones a nivel de modulo sin provocar la caida del servidor principal.
* **RNF-06 (Validacion Estricta y Proteccion DoS):** Todas las entradas HTTP deben validarse mediante esquemas estrictos (Pydantic) con limites de tamano de carga util y limitacion de tasa (*Rate Limiting*).
* **RNF-07 (Trazabilidad y Auditoria):** El sistema debe contar con un mecanismo centralizado de registro de eventos (*logging*) que almacene fecha, hora, modulo y traza de errores para diagnostico rapido.
* **RNF-08 (Transparencia y Control de Dependencias):** Todas las dependencias externas deben estar auditadas y fijadas en `requirements.txt`, evitando librerias no verificadas o puertas traseras, y gestionando credenciales mediante variables de entorno (`.env`).

### Rendimiento y Eficiencia de Costes
* **RNF-09 (Procesamiento Asincrono):** La API debe operar de forma asincrona (FastAPI/Uvicorn) para gestionar peticiones concurrentes sin bloqueos, dejando prevista la integracion de colas de tareas en segundo plano para analisis pesados.
* **RNF-10 (Optimizacion Computacional y Economica):** El flujo de analisis debe minimizar el consumo de recursos y costes de APIs externas priorizando reglas estaticas locales rapidas y el uso de cache antes de invocar modelos de IA.

### Calidad y Ciclo de Vida
* **RNF-11 (Integracion Continua - CI/CD):** El repositorio debe integrar flujos automatizados (GitHub Actions) que ejecuten pruebas unitarias (`pytest`) y validaciones de sintaxis ante cada actualizacion del codigo.
