# Modelado Arquitectónico, Estructural y de Comportamiento

**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG)  
**Versión:** 1.0  
**Referencia:** Estándar UML 2.5 y Modelo C4  

---

## 1. Modelado Arquitectónico (Vista de Contenedores y Componentes - C4)

El modelado arquitectónico define la macroestructura del sistema, mostrando cómo interactúan los clientes externos con el núcleo modular de FastAPI, los motores de análisis y las capas de persistencia.

```mermaid
graph TB
    subgraph Clientes ["Capa de Presentación / Clientes"]
        Web["Frontend Web (Angular)"]
        CLI["Herramienta CLI / IDE"]
    end

    subgraph Backend ["Backend FastAPI (Monolito Modular)"]
        API["API Gateway / Routers (/api/v1)"]
        Orq["Servicio Orquestador (AnalyzerService)"]
        
        subgraph Core ["Núcleo e Infraestructura (core/ & common/)"]
            Config["Configuración (.env)"]
            Logger["Logs Centralizados"]
            Cache["Gestor de Caché (SHA-256)"]
        end

        subgraph Engines ["Subsistema de Motores (Patrón Strategy)"]
            PyEngine["PythonASTEngine"]
            CEngine["CPatternEngine"]
            AIEngine["AIEngine (LLM)"]
        end
    end

    subgraph Datos ["Capa de Datos y Servicios Externos"]
        DB[("Base de Datos Relacional\n(Histórico y Caché)")]
        LLM["Servicio IA / Modelo Local"]
    end

    Web -->|HTTP/JSON| API
    CLI -->|HTTP/JSON| API
    API --> Orq
    Orq --> Cache
    Orq --> PyEngine
    Orq --> CEngine
    Orq --> AIEngine
    Orq --> DB
    AIEngine -->|API / Local| LLM
    Orq -.-> Logger
```

### Principios de esta Vista Arquitectónica:
* **Desacoplamiento de Clientes:** El backend expone una API REST pura, lo que permite añadir interfaces web (Angular) o de consola sin alterar la lógica del servidor.
* **Fronteras de Seguridad:** Toda entrada pasa por la capa de validación (`API`) antes de alcanzar el orquestador (`Orq`).

---

## 2. Modelado Estructural (Diagrama de Clases UML)

El modelado estructural representa la organización estática del código: clases, interfaces abstractas, atributos, métodos y relaciones de herencia o composición.

```mermaid
classDiagram
    class BaseEngine {
        <<abstract>>
        +supported_languages: list~str~
        +engine_name: str
        +scan(code: str, language: str)* list~Vulnerability~
        +supports(language: str) bool
    }

    class PythonASTEngine {
        +supported_languages = ["python"]
        +engine_name = "PythonAST"
        +scan(code: str, language: str) list~Vulnerability~
        -_check_dangerous_calls(tree: AST) list~Vulnerability~
    }

    class CPatternEngine {
        +supported_languages = ["c"]
        +engine_name = "CPattern"
        +scan(code: str, language: str) list~Vulnerability~
        -_check_buffer_overflows(code: str) list~Vulnerability~
    }

    class AIEngine {
        +supported_languages = ["*"]
        +engine_name = "AIAnalyzer"
        +scan(code: str, language: str) list~Vulnerability~
        -_build_security_prompt(code: str, language: str) str
    }

    class EngineFactory {
        -_registry: dict~str, BaseEngine~
        +register_engine(engine: BaseEngine) void
        +get_engines_for_language(language: str) list~BaseEngine~
    }

    class AnalyzerService {
        -factory: EngineFactory
        -repository: ScanRepository
        +analyze_code(request: ScanRequest) ScanResponse
        -_generate_hash(code: str, language: str) str
    }

    class ScanRepository {
        +get_by_hash(code_hash: str) ScanResponse
        +save_scan(scan: ScanResponse) void
        +get_history(limit: int) list~ScanResponse~
    }

    BaseEngine <|-- PythonASTEngine : hereda
    BaseEngine <|-- CPatternEngine : hereda
    BaseEngine <|-- AIEngine : hereda
    EngineFactory o-- BaseEngine : gestiona
    AnalyzerService --> EngineFactory : usa
    AnalyzerService --> ScanRepository : persiste
```

### Elementos Clave de la Estructura:
* **Herencia y Polimorfismo:** `PythonASTEngine`, `CPatternEngine` y `AIEngine` heredan de `BaseEngine`, garantizando que todos implementen el método `.scan()`.
* **Extensibilidad:** Añadir soporte para un nuevo lenguaje (ej. Java o JavaScript) implica únicamente crear una subclase de `BaseEngine` y registrarla en `EngineFactory`.

---

## 3. Modelado de Comportamiento (Diagrama de Secuencia UML)

El modelado de comportamiento describe la dinámica del sistema en tiempo de ejecución: cómo colaboran los objetos paso a paso desde que llega una petición de análisis hasta que se devuelve el informe con remediaciones.

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as Desarrollador (Web/CLI)
    participant Router as AnalyzerRouter
    participant Service as AnalyzerService
    participant Repo as ScanRepository (Caché/BD)
    participant Factory as EngineFactory
    participant Static as StaticEngine (Python/C)
    participant AI as AIEngine

    Cliente->>Router: POST /api/v1/analyze (code, language)
    Router->>Router: Validación estricta (Pydantic)
    Router->>Service: analyze_code(request)
    
    Service->>Service: Calcular SHA-256(code + language)
    Service->>Repo: get_by_hash(code_hash)
    
    alt Resultado existe en Caché
        Repo-->>Service: ScanResponse (guardado)
        Service-->>Router: Retorna informe cacheado
        Router-->>Cliente: 200 OK (JSON instantáneo)
    else No existe en Caché (Análisis nuevo)
        Repo-->>Service: None
        Service->>Factory: get_engines_for_language(language)
        Factory-->>Service: [StaticEngine, AIEngine]
        
        Service->>Static: scan(code, language)
        Static-->>Service: Hallazgos preliminares (Línea, CWE)
        
        opt Análisis profundo / Remediación IA
            Service->>AI: scan(code, language, context=hallazgos)
            alt IA Responde correctamente
                AI-->>Service: Hallazgos enriquecidos + Parche sugerido
            else Fallo o Timeout de IA (Resiliencia)
                AI-->>Service: Excepción controlada (Log error)
                Service->>Service: Conserva hallazgos estáticos
            end
        end
        
        Service->>Repo: save_scan(ScanResponse)
        Service-->>Router: ScanResponse completo
        Router-->>Cliente: 200 OK (JSON estructurado)
    end
```

### Garantías del Flujo de Comportamiento:
1. **Ahorro de Costes (`alt` Caché):** Si el código ya fue escaneado, se cortocircuita el flujo evitando ejecutar motores estáticos o consumir tokens de IA.
2. **Tolerancia a Fallos (`alt` Resiliencia IA):** Si el motor de IA falla o excede el tiempo de espera, el flujo no se interrumpe; el sistema registra el fallo y entrega al usuario los resultados deterministas obtenidos por el motor estático.
