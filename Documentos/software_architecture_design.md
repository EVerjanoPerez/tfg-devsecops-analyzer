# 📐 Documento de Análisis y Diseño de Software
**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG)  
**Estilo Arquitectónico:** Monolito Modular basado en Capas y Patrones Limpios (*Clean Architecture / Modular Monolith*).

---

## 1. Estilo Arquitectónico General
El sistema adopta una **Arquitectura Modular por Dominios**, lo que significa que la aplicación se divide en componentes independientes y auto-contenidos (`modules/`), desacoplados de la infraestructura base (`core/`) y de las utilidades transversales (`common/`). 

Esto garantiza:
* **Bajo acoplamiento y Alta cohesión:** Cada módulo resuelve un problema específico del negocio (ej. `analyzer/`, `reports/`) sin interferir en los demás.
* **Mantenibilidad y Escalabilidad:** Permite modificar, escalar o sustituir cualquier pieza del sistema de forma aislada.

---

## 2. Patrones de Diseño Aplicados
Para cumplir con los requisitos de robustez, flexibilidad y extensibilidad, implementaremos los siguientes patrones de diseño de la ingeniería de software:

### A. Patrón Strategy (Arquitectura de Plugins para Motores de Análisis)
* **Propósito:** Desacoplar la lógica de análisis estático y de IA del núcleo de la aplicación.
* **Implementación:** Se definirá una interfaz o clase base abstracta (`BaseEngine`) que estipule un contrato obligatorio (ej. método `.scan(code: str)`). Los motores concretos (`ASTEngine`, `AIEngine`, etc.) heredarán de esta interfaz. El servicio de análisis elegirá dinámicamente qué motor invocar según la configuración o la complejidad del código.

### B. Patrón Repositorio y Capa de Persistencia (*Repository Pattern*)
* **Propósito:** Aislar la lógica de acceso a la base de datos (histórico de escaneos, metadatos, reportes) de la lógica de negocio.
* **Implementación:** Los servicios no interactúan directamente con las consultas SQL, sino a través de repositorios que gestionan las operaciones contra la base de datos (usando SQLAlchemy / SQLModel).

### C. Inyección de Dependencias (*Dependency Injection*)
* **Propósito:** Proveer instancias de servicios, configuraciones o conexiones de manera controlada y desacoplada.
* **Implementación:** Aprovecharemos el sistema nativo de inyección de dependencias de **FastAPI** (`Depends`), facilitando enormemente las pruebas unitarias (*unit testing*) al poder simular (*mock*) servicios o bases de datos.

---

## 3. Estructura de Capas y Directorios del Proyecto
La organización física en el repositorio reflejará limpiamente este diseño de software:

```text
Codigo/backend/app/
├── main.py                     # Punto de entrada (Inicialización de FastAPI y routers)
├── core/                       # Configuración global y seguridad base
│   ├── config.py               # Variables de entorno (Pydantic BaseSettings)
│   └── database.py             # Conexión y sesión de base de datos
├── common/                     # Utilidades transversales
│   ├── logger.py               # Sistema de logs centralizado (Trazabilidad e histórico)
│   └── exceptions.py           # Manejadores globales de errores defensivos
└── modules/                    # Dominios de negocio aislados
    └── analyzer/               # Módulo Principal de Análisis SAST
        ├── router.py           # Capa HTTP (Endpoints /api/v1/analyze)
        ├── service.py          # Lógica de negocio pura (Orquestación y reglas)
        ├── schemas.py          # Validación estricta de entrada/salida (Pydantic)
        └── engines/            # Subsistema de motores de análisis
            ├── base.py         # Interfaz abstracta (Patrón Strategy)
            ├── ast_engine.py   # Motor de análisis estático tradicional (rápido/gratuito)
            └── ai_engine.py    # Motor basado en Inteligencia Artificial
```

---

## 4. Modelado de Datos y Estructura de Respuesta (El Contrato SAST)
Para asegurar que el analizador no solo detecte fallos, sino que **los clasifique y proponga soluciones técnicas**, la salida de la API (definida en `schemas.py`) devolverá una estructura JSON normalizada por cada vulnerabilidad encontrada:

```json
{
  "scan_id": "uuid-1234-5678",
  "timestamp": "2026-03-03T12:00:00Z",
  "status": "completed",
  "vulnerabilities_found": [
    {
      "title": "Posible Inyección SQL",
      "description": "Se detectó concatenación directa de variables en una consulta SQL.",
      "severity": "CRITICAL",
      "owasp_category": "A03:2021-Injection",
      "cwe_id": "CWE-89",
      "location": {
        "file": "code_snippet.py",
        "line": 14
      },
      "remediation": {
        "explanation": "Utilice consultas parametrizadas o ORMs para evitar la ejecución arbitraria de comandos SQL.",
        "suggested_code": "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
      }
    }
  ]
}
```

---

## 5. Flujo de Datos (Pipeline de Análisis)
El recorrido que sigue una petición desde que el usuario envía el código hasta que recibe el informe es el siguiente:

1. **Ingestión (Router):** FastAPI recibe la petición HTTP POST, y Pydantic valida estrictamente que el tamaño y formato del código sean correctos (prevención de DoS).
2. **Orquestación (Service):** El servicio recibe el código limpio y consulta la caché (por hash SHA-256) para verificar si idéntico código ya fue analizado recientemente.
3. **Ejecución de Motores (Strategy Engines):** 
   * Se ejecuta primero el `ASTEngine` (análisis estático por patrones sintácticos).
   * Si requiere análisis profundo o contextual, se invoca al `AIEngine`.
4. **Enriquecimiento Normativo:** El sistema cruza los hallazgos con la base de conocimiento interna para asociarles su respectivo código **CWE** y categoría **OWASP Top 10**, generando además la propuesta de remediación.
5. **Persistencia y Logs:** Se guarda el resultado en la Base de Datos (histórico de escaneos) y se registra la traza en el sistema de logs centralizado.
6. **Respuesta (Client):** Se devuelve el informe estructurado JSON al cliente (web, app o terminal).

---

## 6. Seguridad, Resiliencia y Calidad
* **Aislamiento de Errores:** Bloques `try-except` controlados a nivel de módulo. Si un motor externo falla, la API responde con un error controlado sin colapsar el servidor.
* **Integración Continua (CI/CD):** Automatización mediante GitHub Actions para ejecutar pruebas unitarias (`pytest`) con cada `git push`.
* **Cero Ejecución Insegura:** El código analizado se procesa exclusivamente de forma estática o en entornos virtuales aislados, blindando el servidor frente a código malicioso.