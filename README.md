# ML-for-Insurance

**Transparencia de modelos de Machine Learning para el cálculo de Reservas Técnicas y RCS bajo el marco CUSF (México)**

> Proyecto de investigación · Facultad de Ciencias, UNAM  
> Autor: Gabriel Fernando Rosas Zepeda  
> Marco regulatorio: Circular Única de Seguros y Fianzas (CUSF) · CNSF · versión compulsada 07-10-2024

---

## Objetivo

La Circular Única de Seguros y Fianzas (CUSF) exige que el **Requerimiento de Capital de Solvencia (RCS)** se calcule al nivel de confianza VaR 99.5% a 1 año, y que las **Reservas Técnicas** (RT = BEL + MR) sean estimadas con métodos actuariales auditables, reproducibles y coherentes con los estándares de la CNSF.

Este proyecto investiga si modelos de Machine Learning pueden **contrastar y complementar** los métodos actuariales estándar reconocidos por la CUSF — Chain Ladder, Bornhuetter-Ferguson, Cape Cod, Mack y Bootstrap — bajo una hipótesis central:

> **Una arquitectura híbrida** (motor actuarial explícito + componente ML interpretable) es la única ruta técnicamente viable para satisfacer los 13 requisitos estructurales de la CUSF Cap. 6.9 que los modelos de caja negra pura no pueden cumplir.

El recorrido completo del proyecto abarca tres dimensiones:

- **Actuarial**: implementar y validar la Fórmula Estándar del RCS con datos reales de la CNSF.
- **Machine Learning**: proponer componentes ML interpretables (GAMs, árboles de profundidad limitada, regresión regularizada) que actúen dentro del marco actuarial, no en lugar de él.
- **Software**: construir un sistema reproducible, versionado y documentado que pueda ser auditado por un experto independiente, satisfaciendo los requisitos de gobierno corporativo de la CUSF.

---

## Contexto regulatorio

| Elemento | Detalle |
|---|---|
| Autoridad | Comisión Nacional de Seguros y Fianzas (CNSF) |
| Marco | Circular Única de Seguros y Fianzas (CUSF) |
| Capítulos clave | 5 (Reservas Técnicas), 8 (RCS Fórmula General), 6.9 (Modelos Internos) |
| Nivel de confianza exigido | VaR 99.5% a 1 año (requisito matemático duro) |
| Reserva Técnica | RT = BEL (Mejor Estimación) + MR (Margen de Riesgo) |
| Métodos reconocidos | Chain Ladder, Bornhuetter-Ferguson, Cape Cod, Mack, Bootstrap |
| Obstáculos para ML puro | 13 requisitos estructurales (estadísticos, auditoría, uso real) |
| Ruta viable | Arquitectura híbrida: ML interpretable dentro de marco actuarial explícito |
| Fuente de datos | [Portal CNSF](https://www.cnsf.gob.mx/EntidadesSupervisadas/InstitucionesSociedadesMutualistas/Paginas/DetalladaSeguros.aspx) |

---

## Estructura del repositorio

```
ML-for-Insurance/
├── .github/
│   └── workflows/
│       └── ci.yml                        ← Tests automáticos en cada push
│
├── docs/
│   ├── Modelos_Reserva_CUSF.pdf          ← Referencia: métodos actuariales y requisitos CUSF
│   ├── Requerimiento_Capital_Solvencia_CUSF.pdf
│   └── notas_tecnicas/                   ← Notas metodológicas por sprint
│
├── data/
│   ├── raw/                              ← Datos originales del portal CNSF (no versionados)
│   ├── processed/                        ← Triángulos de desarrollo y datos limpios
│   └── external/                         ← Curvas libres de riesgo, tablas de correlación RCS
│
├── src/
│   ├── data_io/
│   │   ├── scraper.py                    ← Descarga automatizada del portal CNSF
│   │   └── preprocessor.py              ← Construcción de triángulos de desarrollo
│   │
│   ├── actuarial/                        ← Fórmula Estándar CUSF (Fase 2)
│   │   ├── chain_ladder.py
│   │   ├── bornhuetter_ferguson.py
│   │   ├── cape_cod.py
│   │   ├── mack.py
│   │   └── bootstrap.py
│   │
│   ├── rcs/                              ← Módulos del RCS y VaR 99.5% (Fase 2)
│   │   ├── var_calculator.py
│   │   └── formula_estandar.py
│   │
│   ├── ml/                               ← Modelos internos propuestos (Fase 3)
│   │   ├── interpretable.py             ← GAMs, árboles de profundidad controlada
│   │   └── hibrido.py                   ← ML como estimador dentro del marco actuarial
│   │
│   └── explainability/
│       └── shap_global.py               ← SHAP a nivel de portafolio + atribución de riesgos
│
├── notebooks/
│   ├── 01_exploracion/                   ← EDA: calidad de datos, triángulos iniciales
│   ├── 02_formula_estandar/             ← Chain Ladder, Mack, Bootstrap, BF, Cape Cod
│   ├── 03_rcs_var/                       ← VaR 99.5%, módulos y matrices de correlación
│   ├── 04_ml_interpretable/             ← GAMs, regresión regularizada
│   └── 05_hibrido_validacion/           ← Arquitectura híbrida, back-testing, estrés
│
├── tests/
│   ├── test_chain_ladder.py
│   ├── test_mack.py
│   ├── test_bootstrap.py
│   ├── test_var.py
│   └── test_hibrido.py
│
├── reports/
│   └── figures/                          ← Gráficas generadas por los notebooks
│
├── requirements.txt
├── .gitignore
├── README.md
└── CLAUDE.md                             ← Contexto completo del proyecto para agentes IA
```

---

## Requisitos previos

- **OS**: Debian 12 Bookworm (Linux) — también compatible con cualquier Debian/Ubuntu reciente
- **Python**: 3.11 o superior (`python3 --version`)
- **pip**: incluido con Python 3.11
- **Git**: para clonar el repositorio

---

## Instalación y uso

```bash
# 1. Clonar
git clone https://github.com/<tu-usuario>/ML-for-Insurance.git
cd ML-for-Insurance

# 2. Entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 4. Verificar
python -c "import chainladder, pygam, shap; print('OK — dependencias cargadas')"

# 5. Tests
pytest tests/ -v

# 6. Notebooks
jupyter notebook notebooks/
```

---

## Datos

Los datos de siniestros provienen del **portal oficial de la CNSF**:

```
https://www.cnsf.gob.mx/EntidadesSupervisadas/InstitucionesSociedadesMutualistas/
Paginas/DetalladaSeguros.aspx
```

Ramos disponibles: Vida · Accidentes y Enfermedades · Automóviles

Los archivos descargados se colocan en `data/raw/` y **no se versionan** (ver `.gitignore`). El script de descarga se encuentra en `src/data_io/scraper.py`.

---

## Calendarización del proyecto

El proyecto se desarrolla en **6 meses** bajo un esquema híbrido **Cascada + Scrum ligero**: las tres fases principales (Datos → Actuarial → ML) se ejecutan en secuencia (dependencia lógica entre fases), mientras que dentro de cada fase se trabaja en sprints de 2–3 semanas con entregables concretos y revisión al cierre.

Este esquema es adecuado para un proyecto de investigación individual donde la arquitectura del sistema está clara desde el inicio pero los resultados dentro de cada fase requieren iteración.

### Fases principales

| Fase | Eje | Descripción |
|------|-----|-------------|
| **I** | Datos | Scraping, limpieza y construcción de triángulos de desarrollo con datos reales CNSF |
| **II** | Actuarial | Implementación y validación de la Fórmula Estándar (Chain Ladder, Mack, Bootstrap, BF, Cape Cod) y cálculo del RCS al VaR 99.5% |
| **III** | ML + Híbrido | Modelos ML interpretables como componente de estimación dentro del marco actuarial, validación comparativa y back-testing |

### Calendario (6 meses)

| Mes | Fase | Sprint / Entregable principal | Actuarial | ML | Software |
|-----|------|-------------------------------|:---------:|:--:|:--------:|
| 1 | **I — Datos** | Setup del repo · Scraping automatizado del portal CNSF · EDA y primeros triángulos | — | — | ✓ |
| 2 | **I → II** | Cierre de limpieza de datos · Chain Ladder y BF funcionando sobre datos reales | ✓ | — | ✓ |
| 3 | **II — Actuarial** | Mack + Bootstrap · Cálculo del RCS con Fórmula Estándar · VaR 99.5% verificado | ✓ | — | ✓ |
| 4 | **II → III** | Cape Cod · Cierre de la Fórmula Estándar · Primeros modelos ML interpretables (GAMs) | ✓ | ✓ | ✓ |
| 5 | **III — ML + Híbrido** | Arquitectura híbrida: ML como estimador de frecuencia/severidad en marco actuarial · SHAP global | ✓ | ✓ | ✓ |
| 6 | **III — Validación** | Back-testing · Pruebas de estrés · Benchmarking actuarial vs. híbrido · Memoria técnica final | ✓ | ✓ | ✓ |

> **Convención de estados**: ✓ activo en ese mes · — no iniciado aún

### Estado actual

| Mes | Fase | Estado |
|-----|------|--------|
| 1 | Setup + Scraping CNSF + EDA | ⬜ Pendiente |
| 2 | Limpieza de datos + Chain Ladder + BF | ⬜ Pendiente |
| 3 | Mack + Bootstrap + RCS VaR 99.5% | ⬜ Pendiente |
| 4 | Cape Cod + cierre actuarial + GAMs | ⬜ Pendiente |
| 5 | Arquitectura híbrida + SHAP global | ⬜ Pendiente |
| 6 | Validación + back-testing + memoria técnica | ⬜ Pendiente |

---

## Documentación técnica de referencia

| Documento | Descripción |
|---|---|
| `docs/Modelos_Reserva_CUSF.pdf` | Metodologías aceptadas por la CUSF y los 13 obstáculos estructurales para ML de caja negra |
| `docs/Requerimiento_Capital_Solvencia_CUSF.pdf` | Presentación ejecutiva del RCS, Fórmula General y vías de mitigación para incorporar ML |

---

## Licencia

MIT · Gabriel Fernando Rosas Zepeda · 2026
