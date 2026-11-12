# Modelado Arquitectonico, Estructural y de Comportamiento

**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG)  
**Version:** 1.1  
**Referencia:** Estandar UML 2.5 y Modelo C4  

---

## 1. Modelado Arquitectonico (Vista de Contenedores y Componentes - C4)

El modelado arquitectonico define la macroestructura del sistema, mostrando como interactuan los clientes externos con el nucleo modular de FastAPI, la base de conocimiento desacoplada (`rules/`), los motores de analisis (`EngineRegistry`) y las capas de persistencia.

```mermaid
graph TB
    subgraph Clientes ["Capa de Presentacion / Clientes"]
        Web["Frontend Web (Angular)"]
        CLI["Herramienta CLI / IDE"]
        CICD["Pipeline CI/CD"]
    end

    subgraph Backend ["Backend FastAPI (Monolito Modular)"]
        API["Analyzer Router (/api/v1/analyze)"]
        Orq["AnalyzerService (Orquestador Hibrido)"]
        
        subgraph Core ["Nucleo e Infraestructura (core/ & common/)"]
            Config["Configuracion (.env)"]
            Logger["Logs Centralizados"]
            Cache["Cache Manager (SHA-256 + Rules Version)"]
        end

        subgraph Knowledge ["Base de Conocimiento (rules/)"]
            Meta["metadata.json"]
            PyRules["python_rules.json"]
            CRules["c_rules.json"]
        end

        subgraph Engines ["Motores de Analisis (Patron Strategy)"]
            Registry["EngineRegistry"]
            PyEngine["PythonASTEngine"]
            CEngine["CStaticEngine"]
            AIEngine["AIEngine (LLM)"]
        end
    end

    subgraph Datos ["Capa de Datos y Servicios Externos"]
        DB[("Base de Datos Relacional\n(Histórico y Caché)")]
        LLM["Servicio IA / Modelo Local"]
    end

    Web -->|HTTP/JSON| API
    CLI -->|HTTP/JSON| API
    CICD -->|HTTP/JSON| API
    API --> Orq
    Orq --> Cache
    Orq --> Registry
    Orq --> Meta
    Registry --> PyEngine
    Registry --> CEngine
    Registry --> AIEngine
    PyEngine --> PyRules
    CEngine --> CRules
    Orq --> DB
    AIEngine -->|API / Local| LLM
    Orq -.-> Logger
```

### Principios de esta Vista Arquitectonica:
* **Desacoplamiento de Clientes:** El backend expone una API REST pura, lo que permite anadir interfaces web (Angular), de consola o integraciones CI/CD sin alterar la logica del servidor.
* **Separacion de Motores y Reglas:** Los motores cargan sus definiciones desde `rules/*.json` mediante `RuleLoader`, permitiendo actualizar estandares sin modificar codigo fuente.

---

## 2. Modelado Estructural (Diagrama de Clases UML)

El modelado estructural representa la organizacion estatica del codigo: clases, interfaces abstractas, atributos, metodos y relaciones de herencia o composicion.

```mermaid
classDiagram
    class RuleLoader {
        -rules_dir: Path
        +get_current_version() str
        +load_rules(language: str) list~RuleDefinition~
        +reload() void
    }

    class RuleDefinition {
        +rule_id: str
        +language: str
        +pattern_type: str
        +target: str
        +title: str
        +severity: str
        +owasp_category: str
        +cwe_id: str
        +explanation: str
        +suggested_code: str
    }

    class BaseEngine {
        <<abstract>>
        +name: str
        +supported_languages: list~str~
        #rules: list~RuleDefinition~
        +scan(code: str, language: str)* list~VulnerabilitySchema~
        +supports(language: str) bool
    }

    class PythonASTEngine {
        +name = "PythonASTEngine"
        +supported_languages = ["python"]
        +scan(code: str, language: str) list~VulnerabilitySchema~
        -_evaluate_ast_rules(tree: AST) list~VulnerabilitySchema~
    }

    class CStaticEngine {
        +name = "CStaticEngine"
        +supported_languages = ["c"]
        +scan(code: str, language: str) list~VulnerabilitySchema~
        -_evaluate_pattern_rules(code: str) list~VulnerabilitySchema~
    }

    class AIEngine {
        +name = "AIEngine"
        +supported_languages = ["*"]
        -model_endpoint: str
        +scan(code: str, language: str) list~VulnerabilitySchema~
        -_build_security_prompt(code: str, language: str) str
    }

    class EngineRegistry {
        -_engines: dict~str, list~BaseEngine~~
        +register(engine: BaseEngine) void
        +get_engines_for_language(language: str) list~BaseEngine~
    }

    class AnalyzerService {
        -registry: EngineRegistry
        -repository: ScanRepository
        -rule_loader: RuleLoader
        +analyze_code(request: AnalyzeRequest) AnalyzeResponse
        -_calculate_sha256(code: str) str
    }

    BaseEngine <|-- PythonASTEngine : hereda
    BaseEngine <|-- CStaticEngine : hereda
    BaseEngine <|-- AIEngine : hereda
    BaseEngine o-- RuleDefinition : aplica
    RuleLoader ..> RuleDefinition : instancia
    EngineRegistry o-- BaseEngine : gestiona
    AnalyzerService --> EngineRegistry : consulta
    AnalyzerService --> RuleLoader : verifica version
```

### Elementos Clave de la Estructura:
* **Herencia y Polimorfismo:** `PythonASTEngine`, `CStaticEngine` y `AIEngine` heredan de `BaseEngine`, garantizando que todos implementen el metodo `.scan()`.
* **Extensibilidad Multi-lenguaje:** Anadir soporte para un nuevo lenguaje (ej. Java o JavaScript) implica unicamente crear una subclase de `BaseEngine`, anadir su JSON en `rules/` y registrarla en `EngineRegistry`.

---

## 3. Modelado de Comportamiento (Diagrama de Secuencia UML)

El modelado de comportamiento describe la dinamica del sistema en tiempo de ejecucion: como colaboran los objetos paso a paso desde que llega una peticion de analisis hasta que se devuelve el informe con remediaciones.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Usuario / Cliente
    participant Router as AnalyzerRouter
    participant Service as AnalyzerService
    participant Loader as RuleLoader
    participant Repo as ScanRepository (Cache/BD)
    participant Registry as EngineRegistry
    participant Static as StaticEngine (Python/C)
    participant AI as AIEngine

    Client->>Router: POST /api/v1/analyze (code, language)
    Router->>Router: Validacion estricta (Pydantic)
    Router->>Service: analyze_code(request)
    
    Service->>Service: Calcular SHA-256(code + language)
    Service->>Loader: get_current_version()
    Loader-->>Service: rules_version
    Service->>Repo: find_by_hash_and_version(sha256, rules_version)
    
    alt Resultado existe en Cache vigente
        Repo-->>Service: AnalyzeResponse (guardado)
        Service-->>Router: Retorna informe cacheado
        Router-->>Client: 200 OK (JSON instantaneo)
    else Cache Miss (Analisis nuevo o reglas actualizadas)
        Repo-->>Service: None
        Service->>Registry: get_engines_for_language(language)
        Registry-->>Service: [StaticEngine, AIEngine]
        
        Service->>Static: scan(code, language)
        Static-->>Service: hallazgos_estaticos[]
        
        opt Analisis profundo / Remediacion IA
            Service->>AI: scan(code, language)
            alt IA Responde correctamente
                AI-->>Service: hallazgos_ia[]
            else Fallo o Timeout de IA (Resiliencia)
                AI-->>Service: Excepcion controlada (Log error)
                Service->>Service: Conserva hallazgos estaticos
            end
        end
        
        Service->>Service: Unificar y deduplicar hallazgos
        Service->>Repo: save_scan_result(scan_data, rules_version)
        Service-->>Router: AnalyzeResponse completo
        Router-->>Client: 200 OK (JSON estructurado)
    end
```

### Garantias del Flujo de Comportamiento:
1. **Ahorro de Costes e Invalidacion Inteligente (`alt` Cache):** Si el codigo ya fue escaneado bajo la misma `rules_version`, se devuelve al instante; si las reglas se actualizaron, se re-analiza automaticamente.
2. **Tolerancia a Fallos (`alt` Resiliencia IA):** Si el motor de IA falla o excede el tiempo de espera, el flujo no se interrumpe; el sistema registra el fallo y entrega al usuario los resultados deterministas obtenidos por el motor estatico.
