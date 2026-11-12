# Plan de Pruebas y Aseguramiento de la Calidad (QA)

**Proyecto:** Analizador SAST de Ciberseguridad con IA (TFG)  
**Version:** 1.0  
**Framework de Pruebas:** Pytest + FastAPI TestClient  
**Referencia:** IEEE 829 / Requisitos `RNF-11`  

---

## 1. Estrategia General de Pruebas

Para garantizar la fiabilidad, precision de deteccion y resiliencia del sistema SAST antes de su despliegue o integracion con interfaces cliente, se define una piramide de pruebas automatizadas ejecutables mediante `pytest` y verificadas en cada cambio a traves de GitHub Actions (`RNF-11`).

### Niveles de Prueba
1. **Pruebas Unitarias (Unit Testing):** Verifican de forma aislada los motores de analisis (`PythonASTEngine`, `CStaticEngine`), el cargador de reglas (`RuleLoader`), el registro (`EngineRegistry`) y el calculo de hashes SHA-256.
2. **Pruebas de Integracion (Integration Testing):** Verifican la comunicacion entre capas (`Router` -> `Service` -> `Repository` -> `Base de Datos SQLite en memoria`), comprobando el funcionamiento de la cache versionada y la persistencia.
3. **Pruebas de Seguridad y Resiliencia (Security & Fault Tolerance Testing):** Validan la proteccion contra payloads gigantes (DoS), codigo con errores de sintaxis, aislamiento ante fallos de la IA y ausencia de ejecucion de codigo malicioso.

---

## 2. Matriz de Casos de Prueba Planificados

### A. Pruebas de Motores Estaticos (Python y C)

| ID Prueba | Modulo / Motor | Entrada de Prueba (Snippet) | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| `TC-PY-01` | `PythonASTEngine` | Uso de `eval(user_input)` | Detecta vulnerabilidad `CWE-95` / `OWASP A03:2021`, linea exacta y parche sugerido. |
| `TC-PY-02` | `PythonASTEngine` | Uso de `pickle.loads(data)` | Detecta deserializacion insegura `CWE-502` / `OWASP A08:2021`. |
| `TC-PY-03` | `PythonASTEngine` | Codigo Python limpio y seguro | Devuelve lista vacia `[]` sin falsos positivos. |
| `TC-PY-04` | `PythonASTEngine` | Codigo Python con error de sintaxis (`def broken(:`) | Captura `SyntaxError` de forma controlada sin tumbar el servidor (`RNF-05`). |
| `TC-C-01` | `CStaticEngine` | Uso de `strcpy(dest, src)` o `gets(buf)` | Detecta Buffer Overflow `CWE-120`, linea exacta y alternativa segura (`strncpy` / `fgets`). |
| `TC-C-02` | `CStaticEngine` | Uso de `printf(user_input)` sin formato | Detecta Format String Vulnerability `CWE-134`. |
| `TC-C-03` | `CStaticEngine` | Codigo C limpio usando `fgets` y `snprintf` | Devuelve lista vacia `[]` sin falsos positivos. |

### B. Pruebas de Base de Conocimiento (`rules/`) y Extensibilidad

| ID Prueba | Componente | Escenario | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| `TC-RUL-01` | `RuleLoader` | Carga inicial de `python_rules.json` y `c_rules.json` | Instancia correctamente objetos `RuleDefinition` con version valida de `metadata.json`. |
| `TC-RUL-02` | `EngineRegistry` | Registro de un motor simulado (`MockJavaEngine`) | `get_engines_for_language("java")` devuelve el nuevo motor sin modificar `AnalyzerService`. |

### C. Pruebas de API, Cache Versionada y Seguridad

| ID Prueba | Endpoint / Capa | Escenario | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| `TC-API-01` | `POST /api/v1/analyze` | Envio de snippet valido en Python | HTTP `200 OK` con contrato JSON completo (`scan_id`, `rules_version`, `vulnerabilities_found`). |
| `TC-API-02` | `POST /api/v1/analyze` | Reenvio del mismo snippet con igual `rules_version` | HTTP `200 OK` servido desde cache en tiempo minimo sin re-ejecutar motores. |
| `TC-API-03` | `POST /api/v1/analyze` | Reenvio del mismo snippet tras incrementar `rules_version` | Invalida cache anterior, re-analiza el codigo y guarda nuevo registro con la nueva version. |
| `TC-SEC-01` | `POST /api/v1/analyze` | Envio de payload superior a `MAX_CODE_SIZE_KB` | Rechazo inmediato con HTTP `413` o `422` (Proteccion DoS `RNF-06`). |
| `TC-SEC-02` | `POST /api/v1/analyze` | Envio de codigo Python malicioso (`__import__('os').system('rm -rf')`) | El servidor analiza el AST sin ejecutar el comando; el sistema anfitrion permanece intacto (`RNF-04`). |
| `TC-RES-01` | `AIEngine` (Mock fallo) | Simulacion de caida o timeout en API externa de IA | El sistema captura la excepcion, registra log en `AUDIT_LOGS` y devuelve hallazgos estaticos con `status="partial_error"`. |

---

## 3. Estructura de Archivos de Pruebas (`Codigo/backend/tests/`)

```text
Codigo/backend/tests/
├── __init__.py
├── conftest.py                 # Fixtures de FastAPI TestClient y BD SQLite en memoria
├── test_python_engine.py       # Pruebas TC-PY-01 a TC-PY-04
├── test_c_engine.py            # Pruebas TC-C-01 a TC-C-03
├── test_rules_and_registry.py  # Pruebas TC-RUL-01 a TC-RUL-02
└── test_api_and_security.py    # Pruebas TC-API-01 a TC-RES-01
```
