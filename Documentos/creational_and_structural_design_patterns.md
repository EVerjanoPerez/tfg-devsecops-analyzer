# 🧩 Catálogo de Patrones de Diseño Aplicados

**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG)  
**Versión:** 1.0  
**Referencia:** *Design Patterns: Elements of Reusable Object-Oriented Software* (GoF)  

---

## 1. Introducción
Para asegurar que el sistema cumpla con los requisitos no funcionales de **modularidad (RNF-01)**, **extensibilidad de lenguajes (RNF-02)**, **tolerancia a fallos (RNF-05)** y **optimización de costes (RNF-10)**, la arquitectura incorpora patrones de diseño clásicos clasificados en **Creacionales** y **Estructurales** (complementados con el patrón de comportamiento *Strategy* para la ejecución de algoritmos).

---

## 2. Patrones de Diseño Creacionales
*Se encargan de abstraer el proceso de instanciación de objetos, haciendo que el sistema sea independiente de cómo se crean, componen y representan sus componentes.*

### A. Factory Method / Registry Factory (`EngineFactory`)
* **Problema que resuelve:** El servicio de análisis (`AnalyzerService`) necesita obtener los motores adecuados para analizar un lenguaje concreto (`python`, `c`, etc.), pero no debe conocer los detalles internos de instanciación ni tener bloques condicionales rígidos (`if language == "python": ... elif language == "c": ...`) que obliguen a modificar el núcleo cada vez que se añada un nuevo lenguaje.
* **Solución en el TFG:** Se implementa una fábrica con registro dinámico (`EngineFactory`). Cada motor de análisis se registra indicando los lenguajes que soporta. Cuando llega una petición, el servicio pide a la fábrica: *"dame todos los motores compatibles con este lenguaje"*.
* **Beneficio directo:** Permite añadir soporte para nuevos lenguajes (Java, JS, PHP) simplemente creando una nueva clase y registrándola, cumpliendo el principio **Open/Closed** (abierto a extensión, cerrado a modificación).

### B. Singleton (`Settings` y `Logger`)
* **Problema que resuelve:** Cargar variables de entorno desde el archivo `.env` o abrir manejadores de escritura hacia el archivo centralizado de logs (`app.log`) cada vez que se recibe una petición HTTP generaría sobrecarga de I/O, consumo innecesario de memoria y posibles bloqueos de escritura concurrente.
* **Solución en el TFG:** Mediante decoradores como `@lru_cache()` en `core/config.py` y la gestión centralizada de instancias en `common/logger.py`, se garantiza que exista **una única instancia global** de la configuración y del sistema de registro durante todo el ciclo de vida de la aplicación.
* **Beneficio directo:** Reducción de latencia, coherencia en la configuración global y escritura segura en el histórico de fallos.

### C. Builder / Esquemas Estructurados (`ScanReportBuilder` / Pydantic)
* **Problema que resuelve:** Construir un informe de seguridad complejo que agrupa metadatos del escaneo, múltiples vulnerabilidades, clasificaciones OWASP Top 10, códigos CWE, ubicaciones por línea y fragmentos de código parcheado puede volverse propenso a errores si se manipulan diccionarios sueltos.
* **Solución en el TFG:** Se utiliza un constructor progresivo respaldado por modelos estrictos de Pydantic que va ensamblando las partes del informe (hallazgos estáticos + enriquecimiento de IA + métricas de tiempo) antes de validar y sellar la respuesta final.
* **Beneficio directo:** Garantiza que toda respuesta de la API cumpla al 100% con el contrato JSON esperado por cualquier cliente.

---

## 3. Patrones de Diseño Estructurales
*Se ocupan de cómo se componen las clases y los objetos para formar estructuras más grandes, flexibles y eficientes.*

### A. Facade / Fachada (`AnalyzerService`)
* **Problema que resuelve:** Realizar un escaneo completo implica coordinar múltiples subsistemas complejos: cálculo de hashes SHA-256, consulta a caché, selección de motores mediante fábrica, ejecución de análisis AST, llamadas a IA, mapeo CWE/OWASP y guardado en base de datos. Exponer esta complejidad a los controladores HTTP (`router.py`) ensuciaría el código y dificultaría su reutilización.
* **Solución en el TFG:** `AnalyzerService` actúa como una **Fachada** que ofrece una interfaz única y sencilla (`analyze_code(request)`). Oculta toda la orquestación interna detrás de un único método limpio.
* **Beneficio directo:** El `router.py` queda reducido a unas pocas líneas, y la misma fachada puede ser reutilizada desde una interfaz CLI, una cola de tareas asíncronas o un test unitario.

### B. Adapter / Adaptador (`AIEngineAdapter` y futuros analizadores externos)
* **Problema que resuelve:** Los diferentes proveedores de Inteligencia Artificial (OpenAI, Anthropic, Ollama local) o herramientas externas de seguridad (como `Bandit` o `Cppcheck`) tienen sus propias APIs, formatos de entrada y estructuras de salida incompatibles entre sí.
* **Solución en el TFG:** Cada integración externa se envuelve en una clase **Adaptador** que traduce las peticiones desde nuestro contrato interno (`BaseEngine.scan()`) al formato específico de la herramienta externa, y convierte su respuesta de vuelta a nuestra lista estandarizada de objetos `Vulnerability`.
* **Beneficio directo:** Si mañana decides cambiar de proveedor de IA (por ejemplo, pasar de una API en la nube a un modelo local gratuito para reducir costes), solo cambias el adaptador; el resto del sistema ni se entera.

### C. Proxy de Caché (`CachedAnalyzerProxy`)
* **Problema que resuelve:** Ejecutar análisis sintácticos profundos o invocar modelos de IA tiene un coste computacional y económico significativo si distintos usuarios (o el mismo usuario repetidamente) envían el mismo código fuente.
* **Solución en el TFG:** Se interpone un **Proxy** (o capa interceptora) antes de ejecutar los motores reales. El proxy calcula el hash criptográfico `SHA-256` del código; si el resultado ya existe en la base de datos, devuelve el informe inmediatamente sin invocar a los motores reales.
* **Beneficio directo:** Respuestas instantáneas en milisegundos y reducción drástica del consumo de CPU y presupuesto de APIs.

### D. Decorator / Envoltorio Resiliente (`@safe_engine_execution`)
* **Problema que resuelve:** Si un motor de análisis encuentra un código con sintaxis corrupta o sufre un error inesperado de red, podría lanzar una excepción no controlada que interrumpa el análisis de los demás motores o tumbe la petición HTTP.
* **Solución en el TFG:** Se aplica un patrón **Decorator** (en Python mediante decoradores de función/método) alrededor de la ejecución de cada motor. Este envoltorio captura cualquier excepción, registra la traza completa en `Logger`, y devuelve un resultado vacío o un aviso controlado permitiendo que el resto del sistema siga operando.
* **Beneficio directo:** Cumplimiento estricto del requisito de **Aislamiento de Fallos (RNF-05)**.