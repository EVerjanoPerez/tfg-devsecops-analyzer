# Catalogo de Patrones de Diseno Aplicados

**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG)  
**Version:** 1.1  
**Referencia:** *Design Patterns: Elements of Reusable Object-Oriented Software* (GoF)  

---

## 1. Introduccion
Para asegurar que el sistema cumpla con los requisitos no funcionales de **modularidad (RNF-01)**, **extensibilidad de lenguajes (RNF-02)**, **tolerancia a fallos (RNF-05)**, **optimizacion de costes (RNF-10)** y **desacoplamiento de conocimiento (RNF-12)**, la arquitectura incorpora patrones de diseno clasificados en **Creacionales**, **Estructurales** y de **Comportamiento / Configuracion**.

---

## 2. Patrones de Diseno Creacionales
*Se encargan de abstraer el proceso de instanciacion de objetos, haciendo que el sistema sea independiente de como se crean, componen y representan sus componentes.*

### A. Registry / Factory Method (`EngineRegistry`)
* **Problema que resuelve:** El servicio de analisis (`AnalyzerService`) necesita obtener los motores adecuados para analizar un lenguaje concreto (`python`, `c`, etc.), pero no debe conocer los detalles internos de instanciacion ni tener bloques condicionales rigidos (`if language == "python": ... elif language == "c": ...`) que obliguen a modificar el nucleo cada vez que se anada un nuevo lenguaje.
* **Solución en el TFG:** Se implementa un registro dinamico (`EngineRegistry`). Cada motor de analisis (`PythonASTEngine`, `CStaticEngine`, `AIEngine`) se registra indicando los lenguajes que soporta (`supported_languages`). Cuando llega una peticion, el servicio consulta al registro: *"dame todos los motores compatibles con este lenguaje"*.
* **Beneficio directo:** Permite anadir soporte para nuevos lenguajes (Java, JS, PHP) simplemente creando una nueva clase que herede de `BaseEngine` y registrandola, cumpliendo el principio **Open/Closed** (abierto a extension, cerrado a modificacion).

### B. Singleton (`Settings`, `Logger` y `RuleLoader`)
* **Problema que resuelve:** Cargar variables de entorno desde el archivo `.env`, leer los archivos JSON de reglas en cada peticion HTTP o abrir manejadores de escritura hacia el archivo centralizado de logs (`app.log`) generaria sobrecarga de I/O, consumo innecesario de memoria y posibles bloqueos de escritura concurrente.
* **Solucion en el TFG:** Mediante decoradores como `@lru_cache()` en `core/config.py` y la gestion centralizada de instancias en `common/logger.py` y `rules/loader.py`, se garantiza que exista **una unica instancia global** en memoria de la configuracion, las reglas cargadas (con capacidad de recarga explicita `reload()`) y el sistema de registro.
* **Beneficio directo:** Reduccion de latencia, coherencia en la configuracion global y escritura segura en el historico de fallos.

### C. Builder / Esquemas Estructurados (`AnalyzeResponse` / Pydantic)
* **Problema que resuelve:** Construir un informe de seguridad complejo que agrupa metadatos del escaneo, version de reglas, multiples vulnerabilidades, clasificaciones OWASP Top 10, codigos CWE, ubicaciones por linea y fragmentos de codigo parcheado puede volverse propenso a errores si se manipulan diccionarios sueltos.
* **Solucion en el TFG:** Se utiliza un ensamblado progresivo respaldado por modelos estrictos de Pydantic (`schemas.py`) que valida y sella la respuesta final.
* **Beneficio directo:** Garantiza que toda respuesta de la API cumpla al 100% con el contrato JSON esperado por cualquier cliente.

---

## 3. Patrones de Diseno Estructurales
*Se ocupan de como se componen las clases y los objetos para formar estructuras mas grandes, flexibles y eficientes.*

### A. Facade / Fachada (`AnalyzerService`)
* **Problema que resuelve:** Realizar un escaneo completo implica coordinar multiples subsistemas complejos: calculo de hashes SHA-256, verificacion de version de reglas, consulta a cache, seleccion de motores mediante `EngineRegistry`, ejecucion de analisis AST, llamadas a IA, mapeo CWE/OWASP y guardado en base de datos. Exponer esta complejidad a los controladores HTTP (`router.py`) ensuciaria el codigo y dificultaria su reutilizacion.
* **Solucion en el TFG:** `AnalyzerService` actua como una **Fachada** que ofrece una interfaz unica y sencilla (`analyze_code(request)`). Oculta toda la orquestacion interna detras de un unico metodo limpio.
* **Beneficio directo:** El `router.py` queda reducido a unas pocas lineas, y la misma fachada puede ser reutilizada desde una interfaz CLI, una cola de tareas asincronas o un test unitario.

### B. Adapter / Adaptador (`AIEngine` y futuros analizadores externos)
* **Problema que resuelve:** Los diferentes proveedores de Inteligencia Artificial (OpenAI, Anthropic, Ollama local) o herramientas externas de seguridad tienen sus propias APIs, formatos de entrada y estructuras de salida incompatibles entre si.
* **Solucion en el TFG:** Cada integracion externa se envuelve en una clase **Adaptador** que traduce las peticiones desde nuestro contrato interno (`BaseEngine.scan()`) al formato especifico de la herramienta externa, y convierte su respuesta de vuelta a nuestra lista estandarizada de objetos `VulnerabilitySchema`.
* **Beneficio directo:** Si manana decides cambiar de proveedor de IA (por ejemplo, pasar de una API en la nube a un modelo local gratuito para reducir costes), solo cambias el adaptador; el resto del sistema ni se entera.

### C. Proxy de Cache Versionada (`ScanRepository` / Interceptor en `AnalyzerService`)
* **Problema que resuelve:** Ejecutar analisis sintacticos profundos o invocar modelos de IA tiene un coste computacional y economico significativo si distintos usuarios envian el mismo codigo fuente, pero devolver resultados cacheados tras actualizar reglas de seguridad seria peligroso.
* **Solucion en el TFG:** Se interpone una verificacion previa antes de ejecutar los motores reales comprobando el par `(code_hash, rules_version)`. Si existe coincidencia exacta, devuelve el informe inmediatamente sin invocar a los motores.
* **Beneficio directo:** Respuestas instantaneas en milisegundos con invalidacion automatica ante actualizaciones de reglas.

### D. Decorator / Envoltorio Resiliente (`@safe_engine_execution`)
* **Problema que resuelve:** Si un motor de analisis encuentra un codigo con sintaxis corrupta o sufre un error inesperado de red, podria lanzar una excepcion no controlada que interrumpa el analisis de los demas motores o tumbe la peticion HTTP.
* **Solucion en el TFG:** Se aplica un patron **Decorator** alrededor de la ejecucion de cada motor. Este envoltorio captura cualquier excepcion, registra la traza completa en `Logger`, y devuelve un resultado vacio o un aviso controlado permitiendo que el resto del sistema siga operando.
* **Beneficio directo:** Cumplimiento estricto del requisito de **Aislamiento de Fallos (RNF-05)**.

---

## 4. Patrones de Comportamiento y Configuracion Externa

### A. Strategy (`BaseEngine`)
* **Problema que resuelve:** Cada lenguaje de programacion requiere tecnicas de analisis completamente distintas (arboles sintacticos `ast` en Python, analisis de punteros y memoria en C, analisis semantico con LLM).
* **Solucion en el TFG:** La clase abstracta `BaseEngine` define la familia de algoritmos intercambiables bajo una firma comun (`scan(code, language)`), permitiendo que `AnalyzerService` ejecute polimorficamente cualquier estrategia sin conocer su implementacion interna.

### B. Externalized Knowledge Base (Reglas como Datos Versionados en `rules/`)
* **Problema que resuelve:** Las definiciones de vulnerabilidades, categorias OWASP Top 10 y codigos CWE cambian con el tiempo. Incrustarlos en el codigo obligaria a modificar y redesplegar los motores.
* **Solucion en el TFG:** `RuleLoader` carga archivos JSON externos (`metadata.json`, `python_rules.json`, `c_rules.json`) e instancia objetos `RuleDefinition` que son consumidos por los motores estaticos.
