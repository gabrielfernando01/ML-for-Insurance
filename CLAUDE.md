# CLAUDE.md — Contexto completo del proyecto para agentes de IA

> Este archivo está diseñado para ser leído por agentes de IA (Claude, Copilot, Cursor, etc.)  
> antes de interactuar con cualquier parte del repositorio. Contiene el contexto técnico,  
> regulatorio y arquitectónico completo del proyecto.

---

## 1. ¿Qué es este proyecto?

**ML-for-Insurance** es un proyecto de investigación de la Facultad de Ciencias, UNAM, que investiga si modelos de Machine Learning pueden contrastar y complementar los métodos actuariales estándar exigidos por la CNSF para el cálculo de:

- **Reservas Técnicas** = Mejor Estimación (BEL) + Margen de Riesgo (MR)
- **Requerimiento de Capital de Solvencia (RCS)** al 99.5% VaR a 1 año

La hipótesis central es que una **arquitectura híbrida** — motor actuarial explícito + componente ML interpretable — es la única ruta viable para satisfacer los 13 requisitos estructurales de la CUSF Cap. 6.9 que los modelos de caja negra pura no pueden cumplir.

El proyecto opera simultáneamente en tres ejes:

| Eje | Qué resuelve | Artefactos principales |
|-----|-------------|------------------------|
| **Actuarial** | Implementar y validar la Fórmula Estándar del RCS con datos reales CNSF | `src/actuarial/`, `src/rcs/`, `notebooks/02_*/`, `notebooks/03_*/` |
| **Machine Learning** | Proponer componentes ML interpretables dentro del marco actuarial | `src/ml/`, `src/explainability/`, `notebooks/04_*/`, `notebooks/05_*/` |
| **Software** | Garantizar reproducibilidad, auditabilidad y calidad de código | `src/`, `tests/`, `.github/workflows/`, `CLAUDE.md` |

---

## 2. Marco regulatorio relevante

| Elemento | Detalle |
|---|---|
| Autoridad | Comisión Nacional de Seguros y Fianzas (CNSF) |
| Marco | Circular Única de Seguros y Fianzas (CUSF) · versión compulsada 07-10-2024 |
| Capítulos críticos | Cap. 5 (Reservas Técnicas), Cap. 8 (RCS Fórmula General), Cap. 6.9 (Modelos Internos) |
| Nivel de confianza | VaR 99.5% a 1 año — requisito matemático duro, no negociable |
| Métodos reconocidos | Chain Ladder, Bornhuetter-Ferguson, Cape Cod, Mack, Bootstrap |
| Obstáculo central | 13 requisitos estructurales que ML de caja negra no puede satisfacer |

### Los 13 requisitos CUSF Cap. 6.9 (resumen)

**Estadísticos y metodológicos (6):** distribución de probabilidad al 99.5%, reproducibilidad por experto independiente, hipótesis y parámetros explícitos, back-testing y atribución de P&L, coherencia con estándares actuariales (IAA/IASB/CNSF), demostración de equivalencia al 99.5%.

**Auditoría y gobierno corporativo (7):** comprensión por el Consejo de Administración, explicación por responsables del modelo, transparencia en P&L por segmento, auditoría interna efectiva, revisión externa anual por experto, opinión favorable del experto, control de versiones auditable.

**Prueba de utilización (2):** uso real en toma de decisiones ≥ 1 año, pruebas de estrés interpretables por el Consejo.

---

## 3. Arquitectura del código

### Principios de diseño

1. **Separación de responsabilidades**: cada módulo en `src/` tiene una sola función. Los notebooks consumen módulos; no contienen lógica de negocio.
2. **Reproducibilidad total**: dado el mismo dataset en `data/processed/`, cualquier resultado debe ser replicable ejecutando los tests o los notebooks en orden.
3. **Auditabilidad**: cada función expone sus hipótesis y parámetros. Nada implícito.
4. **Testabilidad**: toda función con lógica actuarial o estadística tiene su test en `tests/`.

### Flujo de datos

```
Portal CNSF
    │
    ▼
src/data_io/scraper.py          ← descarga automatizada
    │
    ▼
src/data_io/preprocessor.py     ← construcción de triángulos de desarrollo
    │
    ▼
data/processed/                 ← triángulos limpios (input canónico)
    │
    ├──▶ src/actuarial/          ← Chain Ladder, Mack, Bootstrap, BF, Cape Cod
    │         │
    │         ▼
    │    src/rcs/                ← VaR 99.5%, módulos y matrices de correlación
    │
    └──▶ src/ml/                 ← GAMs, árboles, modelo híbrido
              │
              ▼
         src/explainability/     ← SHAP global + atribución de riesgos
```

---

## 4. Por qué este proyecto es un producto de software

Esta sección es la más importante para entender el alcance real del proyecto. No se trata solo de notebooks de análisis: se trata de un sistema con garantías de calidad, trazabilidad y despliegue.

### 4.1 CI/CD como columna vertebral de la auditabilidad

El archivo `.github/workflows/ci.yml` no es un detalle técnico secundario. Es la respuesta concreta a uno de los 13 requisitos más difíciles de la CUSF Cap. 6.9: **el control de versiones auditable**.

La CUSF exige que un modelo interno pueda ser auditado en cualquier momento por un experto independiente. Eso implica que:

- El modelo que calculó el RCS del trimestre pasado debe poder reproducirse exactamente.
- Cualquier cambio al modelo debe dejar traza.
- El sistema debe fallar de forma explícita si una modificación rompe una garantía actuarial.

**El pipeline de CI/CD resuelve esto de la siguiente manera:**

```
Cada push o pull request al repositorio dispara automáticamente:

  1. Instalación del entorno (requirements.txt)
        ↓
  2. Ejecución de pytest tests/ -v
        │
        ├── test_chain_ladder.py   → verifica factores de desarrollo y proyección IBNR
        ├── test_mack.py           → verifica varianza e intervalos de confianza del BEL
        ├── test_bootstrap.py      → verifica distribuciones empíricas del IBNR
        ├── test_var.py            → verifica que el VaR 99.5% esté dentro de tolerancia
        └── test_hibrido.py        → verifica que el modelo híbrido no rompa la coherencia actuarial
        ↓
  3. El commit solo puede mergearse si todos los tests pasan

```

Esto significa que **ninguna versión del modelo que rompa una garantía actuarial puede llegar a producción**. Ese es el significado real del CI/CD en este contexto: no es automatización por comodidad, es automatización como mecanismo de cumplimiento regulatorio.

### 4.2 Lo que distingue "análisis" de "software"

| Característica | Notebook ad hoc | Este proyecto |
|---|---|---|
| Reproducibilidad | Depende del entorno local | Garantizada por CI en cada commit |
| Trazabilidad | Ninguna | Git history + CI log por versión |
| Verificación | Manual | Automatizada con pytest |
| Modificación segura | El autor sabe qué rompe qué | Los tests fallan si algo se rompe |
| Auditoría externa | Imposible sin el autor | Cualquier experto clona y ejecuta |
| Despliegue | No aplica | Base para API o aplicación interactiva |

La diferencia entre un análisis y un producto de software es que el producto **puede ser operado, verificado y mantenido por alguien distinto a quien lo construyó**. Eso es exactamente lo que exige la CUSF para los modelos internos.

### 4.3 Versionado semántico del modelo

Cada versión del sistema (cambio en parámetros, nuevos datos, nuevo método) debe etiquetarse siguiendo versionado semántico:

```
v{MAJOR}.{MINOR}.{PATCH}

MAJOR → cambio en metodología actuarial o estructura del RCS
MINOR → nuevo ramo de datos, nuevo modelo ML, nuevo módulo
PATCH → corrección de bug, ajuste de parámetro, actualización de datos
```

Cada tag de Git corresponde a un estado auditable del sistema completo. Un experto independiente puede hacer `git checkout v1.2.0` y reproducir exactamente el cálculo del RCS de ese período.

---

## 5. Instrucciones para agentes de IA

Si eres un agente de IA trabajando en este repositorio, sigue estas reglas:

**Siempre:**
- Mantén la separación entre `src/` (lógica) y `notebooks/` (exploración).
- Agrega o modifica tests en `tests/` cuando modifiques lógica en `src/`.
- Documenta hipótesis actuariales en docstrings, no solo en comentarios.
- Usa la curva libre de riesgo CNSF de `data/external/` para descuentos; no uses proxies.

**Nunca:**
- Pongas lógica de negocio actuarial directamente en un notebook.
- Modifiques `data/processed/` manualmente; usa siempre el pipeline de `src/data_io/`.
- Uses modelos de caja negra (redes neuronales profundas, XGBoost sin restricciones) como motor principal del RCS; solo como componente de estimación dentro del marco actuarial.
- Hagas hardcode de parámetros regulatorios (tasa de costo de capital, matrices de correlación); cárgalos siempre desde `data/external/`.

**Al agregar un nuevo modelo:**
1. Impleméntalo en `src/ml/` o `src/actuarial/` según corresponda.
2. Escribe su test en `tests/`.
3. Verifica que pasa el pipeline completo de CI localmente con `pytest tests/ -v`.
4. Documenta sus hipótesis y limitaciones regulatorias en el docstring de la clase.

---

## 6. Del repositorio a una aplicación interactiva

El diseño modular de `src/` hace que el paso de "repositorio de investigación" a "aplicación desplegada" sea una extensión natural, no una reescritura. Esta sección describe esa ruta.

### 6.1 Capa de API (FastAPI)

El primer paso es exponer los módulos de `src/` como endpoints HTTP. Cada función principal del sistema se convierte en una ruta:

```
POST /actuarial/chain-ladder
     body: { triangulo: [[...]], metodo: "volumen" }
     response: { ibnr: float, factores: [...], bel: float }

POST /actuarial/mack
     body: { triangulo: [[...]] }
     response: { bel: float, varianza: float, intervalo_95: [float, float] }

POST /rcs/var
     body: { distribucion: [...], nivel_confianza: 0.995 }
     response: { rcs: float, var_99_5: float, modulos: {...} }

POST /ml/hibrido
     body: { triangulo: [[...]], ramo: "automoviles" }
     response: { bel_actuarial: float, bel_hibrido: float, shap_values: {...} }

GET  /datos/ramos
     response: { ramos: ["vida", "autos", "acc_enf"], periodos_disponibles: [...] }
```

Con FastAPI, cada endpoint hereda automáticamente la documentación de los docstrings de `src/`. El resultado es una API auto-documentada que cualquier consumidor (panel web, hoja de cálculo, sistema institucional) puede invocar.

### 6.2 Arquitectura de despliegue

```
                        ┌─────────────────────────────────┐
                        │         Usuario final            │
                        │  (actuario, analista, regulador) │
                        └────────────┬────────────────────┘
                                     │ HTTPS
                        ┌────────────▼────────────────────┐
                        │      Panel Interactivo           │
                        │   Streamlit · Dash · Panel       │
                        │  (configuración dinámica de      │
                        │   parámetros y visualización)    │
                        └────────────┬────────────────────┘
                                     │ REST / WebSocket
                        ┌────────────▼────────────────────┐
                        │         FastAPI                  │
                        │    (expone src/ como API)        │
                        └──────┬───────────────┬──────────┘
                               │               │
                  ┌────────────▼──┐     ┌──────▼────────────┐
                  │  src/actuarial │     │     src/ml/        │
                  │  src/rcs/      │     │  src/explainability│
                  └────────────┬──┘     └──────┬────────────┘
                               │               │
                        ┌──────▼───────────────▼──────┐
                        │        data/processed/       │
                        │    (triángulos CNSF limpios) │
                        └─────────────────────────────┘
```

### 6.3 El panel interactivo: qué podría tocar un usuario

El valor de una interfaz interactiva en este contexto no es cosmético. Es que un actuario o regulador puede **explorar el espacio de parámetros en tiempo real** sin escribir código, y ver cómo cada decisión de modelado afecta el RCS y las reservas.

**Configuraciones dinámicas que tendría sentido exponer:**

```
┌─────────────────────────────────────────────────────────────┐
│  PANEL DE CONFIGURACIÓN                                      │
├─────────────────────────────────────────────────────────────┤
│  Ramo:           [ Automóviles ▼ ]                          │
│  Período:        [ 2019–2023   ▼ ]                          │
│  Método base:    [ Chain Ladder ▼ ] [ Mack ] [ Bootstrap ]  │
│                                                             │
│  ── Parámetros del RCS ──────────────────────────────────── │
│  Nivel de confianza:   [  99.5 %  ] (fijo CUSF)            │
│  Tasa costo capital:   [  10.0 %  ] (ajustable)            │
│  Horizonte:            [  1 año   ] (fijo CUSF)            │
│                                                             │
│  ── Modelo híbrido ─────────────────────────────────────── │
│  Activar componente ML:    [ ✓ ]                           │
│  Tipo de modelo ML:        [ GAM ▼ ]                       │
│  Profundidad máx. árbol:   [  3   ] (si aplica)            │
│  Mostrar SHAP values:      [ ✓ ]                           │
│                                                             │
│              [ ▶  EJECUTAR CÁLCULO ]                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  RESULTADOS                                                  │
├──────────────────────┬──────────────────────────────────────┤
│  BEL (actuarial)     │  $ 142,350,000                       │
│  BEL (híbrido)       │  $ 139,820,000  (−1.8%)             │
│  Margen de Riesgo    │  $  18,400,000                       │
│  Reserva Técnica     │  $ 158,220,000                       │
│  RCS (VaR 99.5%)     │  $  47,600,000                       │
├──────────────────────┴──────────────────────────────────────┤
│  [Triángulo de desarrollo]  [Distribución IBNR]             │
│  [Atribución SHAP]          [Comparativo métodos]           │
│  [Exportar a PDF / Excel]                                   │
└─────────────────────────────────────────────────────────────┘
```

**Por qué esto importa regulatoriamente:** uno de los requisitos de la CUSF para modelos internos es que el Consejo de Administración comprenda el modelo y que las pruebas de estrés sean interpretables por directivos no técnicos. Un panel de este tipo convierte un resultado de código en una herramienta de gobierno corporativo.

### 6.4 Stack tecnológico sugerido

| Capa | Opción principal | Alternativa |
|------|-----------------|-------------|
| Panel interactivo | **Streamlit** (prototipo rápido, Python nativo) | Dash (más control sobre UI) |
| API backend | **FastAPI** | Flask |
| Servidor | **Render / Railway** (gratuito para investigación) | VPS con Docker |
| Autenticación | **HTTP Basic** (suficiente para investigación) | Auth0 para producción |
| Exportación | **WeasyPrint** (PDF desde HTML) | ReportLab |
| Contenerización | **Docker + docker-compose** | Bare metal |

### 6.5 Ruta de madurez del producto

El diseño actual del repositorio permite crecer en etapas sin reescribir:

```
Fase actual       →   Repositorio de investigación con CI/CD
                            ↓
Extensión natural →   FastAPI sobre src/ + Streamlit básico
                            ↓
Producto maduro   →   Panel multi-ramo + autenticación + exportación PDF
                            ↓
Producto regulatorio →  API certificable por auditor externo
                         (los tests de CI son la evidencia de control)
```

En cada etapa, **el mismo código de `src/` es el núcleo**. El CI/CD garantiza que cualquier extensión no rompe las garantías actuariales ya probadas. Eso es lo que hace que sea un producto de software y no solo un análisis: la arquitectura permite crecer con confianza.

---

## 7. Contacto y contexto académico

| Campo | Detalle |
|---|---|
| Autor | Gabriel Fernando Rosas Zepeda |
| Institución | Facultad de Ciencias, UNAM |
| Marco | Proyecto de investigación · 2026 |
| Regulador | CNSF · Circular Única de Seguros y Fianzas (CUSF) |
| Versión CUSF | Compulsada al 07-10-2024 |
