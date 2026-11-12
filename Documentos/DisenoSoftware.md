# Documento de Analisis y Diseno de Software

**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG)  
**Version:** 1.1  
**Estilo Arquitectonico:** Monolito Modular basado en Capas y Patrones Limpios (*Clean Architecture / Modular Monolith*).  

---

## 1. Estilo Arquitectonico General

El sistema adopta una **Arquitectura Modular por Dominios**, lo que significa que la aplicacion se divide en componentes independientes y auto-contenidos (`modules/`), desacoplados de la infraestructura base (`core/`) y de las utilidades transversales (`common/`).

Esto garantiza:
* **Bajo acoplamiento y Alta cohesion:** Cada modulo resuelve un problema especifico del negocio (ej. `analyzer/`) sin interferir en los demas.
* **Mantenibilidad y Escalabilidad:** Permite modificar, escalar o sustituir cualquier pieza del sistema de forma aislada.
* **Actualizacion Dinamica de Conocimiento:** Separacion total entre los motores de ejecucion y las bases de conocimiento de vulnerabilidades (`rules/`).

---

## 2. Patrones de Diseno Aplicados

Para cumplir con los requisitos de robustez, flexibilidad y extensibilidad, implementaremos los siguientes patrones de diseno de la ingenieria de software:

### A. Patron Strategy (Arquitectura de Plugins para Motores de Analisis)
* **Proposito:** Desacoplar la logica de analisis estatico y de IA del nucleo de la aplicacion.
* **Implementacion:** Se definira una interfaz o clase base abstracta (`BaseEngine`) que estipule un contrato obligatorio (metodo `.scan(code: str, language: str)`). Los motores concretos (`PythonASTEngine`, `CStaticEngine`, `AIEngine`) heredaran de esta interfaz y seran gestionados dinamicamente por `EngineRegistry`.

### B. Externalized Knowledge Base (Reglas como Datos Versionados)
* **Proposito:** Evitar que los patrones de ataque, mapeos OWASP/CWE y plantillas de solucion esten incrustados (*hardcoded*) en el codigo fuente.
* **Implementacion:** Un cargador (`RuleLoader`) lee definiciones externas en formato JSON desde `modules/analyzer/rules/`, permitiendo actualizar estandares (ej. nuevas versiones de OWASP Top 10 o CWE) sin modificar los motores.

### C. Patron Repositorio y Capa de Persistencia (*Repository Pattern*)
* **Proposito:** Aislar la logica de acceso a la base de datos (historico de escaneos, cache versionada, auditoria) de la logica de negocio.
* **Implementacion:** Los servicios interactuan exclusivamente a traves de `ScanRepository` (usando SQLAlchemy / SQLModel).

### D. Inyeccion de Dependencias (*Dependency Injection*)
* **Proposito:** Proveer instancias de servicios, configuraciones o conexiones de manera controlada y desacoplada.
* **Implementacion:** Uso del sistema nativo `Depends` de **FastAPI**, facilitando las pruebas unitarias (*unit testing*) mediante *mocks*.

---

## 3. Estructura de Capas y Directorios del Proyecto

La organizacion fisica en el repositorio reflejara limpiamente este diseno de software:

```text
Codigo/backend/app/
├── main.py                         # Punto de entrada (Inicializacion de FastAPI y routers)
├── core/                           # Configuracion global y seguridad base
│   ├── config.py                   # Variables de entorno (Pydantic BaseSettings)
│   └── database.py                 # Conexion y sesion de base de datos
├── common/                         # Utilidades transversales
│   ├── logger.py                   # Sistema de logs centralizado (Trazabilidad e historico)
│   └── exceptions.py               # Manejadores globales de errores defensivos
└── modules/                        # Dominios de negocio aislados
    └── analyzer/                   # Modulo Principal de Analisis SAST
        ├── router.py               # Capa HTTP (Endpoints /api/v1/analyze)
        ├── service.py              # Logica de negocio pura (Orquestacion y reglas)
        ├── schemas.py              # Validacion estricta de entrada/salida (Pydantic)
        ├── repository.py           # Persistencia y busqueda en cache (code_hash + rules_version)
        ├── rules/                  # Base de conocimiento desacoplada y versionada
        │   ├── loader.py           # RuleLoader (carga y hot-reload de definiciones JSON)
        │   ├── metadata.json       # Version activa de reglas y estandares (ej. OWASP 2021)
        │   ├── python_rules.json   # Reglas AST/patrones para Python, CWE, OWASP y parches
        │   └── c_rules.json        # Reglas estaticas para C, CWE, OWASP y parches
        └── engines/                # Subsistema de motores de analisis
            ├── base.py             # Interfaz abstracta (Patron Strategy)
            ├── registry.py         # Registro dinamico de motores por lenguaje
            ├── python_ast_engine.py# Motor AST para Python
            ├── c_static_engine.py  # Motor estatico para C
            └── ai_engine.py        # Motor basado en Inteligencia Artificial
```

---

## 4. Modelado de Datos y Estructura de Respuesta (El Contrato SAST)

Para asegurar que el analizador no solo detecte fallos, sino que **los clasifique y proponga soluciones tecnicas**, la salida de la API (definida en `schemas.py`) devolvera una estructura JSON normalizada por cada vulnerabilidad encontrada:

```json
{
  "scan_id": "uuid-1234-5678",
  "rules_version": "1.0.0-owasp2021",
  "timestamp": "2026-03-03T12:00:00Z",
  "status": "completed",
  "vulnerabilities_found": [
    {
      "title": "Posible Inyeccion SQL",
      "description": "Se detecto concatenacion directa de variables en una consulta SQL.",
      "severity": "CRITICAL",
      "owasp_category": "A03:2021-Injection",
      "cwe_id": "CWE-89",
      "location": {
        "file": "code_snippet.py",
        "line": 14
      },
      "remediation": {
        "explanation": "Utilice consultas parametrizadas o ORMs para evitar la ejecucion arbitraria de comandos SQL.",
        "suggested_code": "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
      }
    }
  ]
}
```

---

## 5. Flujo de Datos (Pipeline de Analisis)

El recorrido que sigue una peticion desde que el usuario envia el codigo hasta que recibe el informe es el siguiente:

1. **Ingestion (Router):** FastAPI recibe la peticion HTTP POST, y Pydantic valida estrictamente que el tamano y formato del codigo sean correctos (prevencion de DoS).
2. **Orquestacion y Cache Versionada (Service):** El servicio calcula el hash SHA-256 del codigo, obtiene la version vigente de reglas (`RuleLoader.get_current_version()`) y consulta la cache verificando coincidencia exacta de `(code_hash, rules_version)`. Si existe, devuelve el resultado al instante.
3. **Ejecucion de Motores (Strategy Engines):** 
   * Se ejecutan primero los motores estaticos registrados para el lenguaje (`PythonASTEngine` o `CStaticEngine`), aplicando las definiciones cargadas desde `rules/`.
   * Si se requiere analisis contextual profundo, se invoca al `AIEngine`.
4. **Enriquecimiento Normativo:** Los motores cruzan los hallazgos con la base de conocimiento `rules/` para asociarles su respectivo codigo **CWE**, categoria **OWASP Top 10** vigente y plantilla de solucion sin codigo *hardcoded*.
5. **Persistencia y Logs:** Se guarda el resultado en la Base de Datos junto con la version de reglas utilizada y se registra la traza en el sistema de logs centralizado.
6. **Respuesta (Client):** Se devuelve el informe estructurado JSON al cliente (web, app o terminal).

---

## 6. Seguridad, Resiliencia y Calidad

* **Aislamiento de Errores:** Bloques `try-except` controlados a nivel de modulo. Si un motor externo falla, la API responde con un error controlado sin colapsar el servidor.
* **Integracion Continua (CI/CD):** Automatizacion mediante GitHub Actions para ejecutar pruebas unitarias (`pytest`) con cada `git push`.
* **Cero Ejecucion Insegura:** El codigo analizado se procesa exclusivamente de forma estatica o en entornos virtuales aislados, blindando el servidor frente a codigo malicioso.
