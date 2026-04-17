# ML-for-Insurance

**Transparencia de modelos de Machine Learning para el cálculo de Reservas Técnicas y RCS bajo el marco CUSF (México)**

> Proyecto de investigación · Facultad de Ciencias, UNAM  
> Autor: Gabriel Fernando Rosas Zepeda  
> Marco regulatorio: Circular Única de Seguros y Fianzas (CUSF) · CNSF · versión compulsada 07-10-2024

---

## Objetivo

Este repositorio investiga si modelos de Machine Learning pueden contrastar —y eventualmente complementar— los métodos actuariales estándar exigidos por la CNSF para el cálculo de:

1. **Reserva Técnica** = Mejor Estimación (BEL) + Margen de Riesgo (MR)
2. **Requerimiento de Capital de Solvencia (RCS)** al 99.5 % VaR a 1 año

La hipótesis central es que una **arquitectura híbrida** (modelo actuarial explícito + componente ML interpretable) es la única ruta viable para satisfacer los 13 requisitos de la CUSF Cap. 6.9 que los modelos de caja negra pura no pueden cumplir.

---

## Contexto regulatorio

| Elemento | Detalle |
|---|---|
| Autoridad | Comisión Nacional de Seguros y Fianzas (CNSF) |
| Marco | Circular Única de Seguros y Fianzas (CUSF) |
| Capítulos clave | 5 (Reservas), 8 (RCS Fórmula General), 6.9 (Modelos Internos) |
| Nivel de confianza exigido | VaR 99.5 % a 1 año (requisito matemático duro) |
| Métodos reconocidos | Chain Ladder, Bornhuetter-Ferguson, Cape Cod, Mack, Bootstrap |
| Fuente de datos | [Portal CNSF](https://www.cnsf.gob.mx/EntidadesSupervisadas/InstitucionesSociedadesMutualistas/Paginas/DetalladaSeguros.aspx) |

---

## Estructura del repositorio

```
ML-for-Insurance/
├── .github/
│   └── workflows/
│       └── ci.yml                  ← Tests automáticos en cada push
│
├── docs/
│   ├── Modelos_Reserva_CUSF.pdf    ← Documento técnico de referencia
│   ├── Requerimiento_Capital_Solvencia_CUSF.pdf
│   └── notas_tecnicas/             ← Notas metodológicas por sprint
│
├── data/
│   ├── raw/                        ← Datos originales descargados del portal CNSF (no se versionan)
│   ├── processed/                  ← Triángulos de desarrollo y datos limpios
│   └── external/                   ← Curvas libres de riesgo CNSF, tablas de correlación RCS
│
├── notebooks/
│   ├── 01_exploracion/             ← EDA: calidad de datos, triángulos iniciales
│   ├── 02_actuarial/               ← Chain Ladder, Mack, Bootstrap, BF, Cape Cod
│   ├── 03_rcs_var/                 ← Fórmula General RCS, VaR 99.5 %, módulos de riesgo
│   ├── 04_ml_interpretable/        ← GAMs, árboles limitados, regresión regularizada
│   ├── 05_hibrido/                 ← Arquitectura híbrida actuarial + ML
│   └── 06_validacion/              ← Back-testing, atribución P&L, pruebas de estrés
│
├── src/
│   ├── actuarial/
│   │   ├── chain_ladder.py         ← Implementación y wrappers de chainladder library
│   │   ├── bornhuetter_ferguson.py
│   │   ├── cape_cod.py
│   │   ├── mack.py                 ← Varianza e intervalos de confianza del BEL
│   │   └── bootstrap.py            ← Distribuciones empíricas del IBNR
│   ├── rcs/
│   │   ├── var_calculator.py       ← VaR 99.5 % sobre distribuciones de pérdidas
│   │   └── formula_estandar.py     ← Módulos y matrices de correlación CUSF
│   ├── ml/
│   │   ├── interpretable.py        ← GAMs (pygam), árboles de profundidad controlada
│   │   └── hibrido.py              ← ML como estimador de frecuencia/severidad en marco actuarial
│   ├── explainability/
│   │   └── shap_global.py          ← SHAP a nivel portafolio completo + atribución de riesgos
│   ├── data_io/
│   │   ├── loader.py               ← Descarga y lectura de datos portal CNSF
│   │   └── preprocessor.py         ← Construcción de triángulos de desarrollo
│   └── utils/
│       └── helpers.py              ← Funciones auxiliares compartidas
│
├── tests/
│   ├── test_chain_ladder.py
│   ├── test_mack.py
│   ├── test_bootstrap.py
│   ├── test_var.py
│   └── test_hibrido.py
│
├── reports/
│   └── figures/                    ← Gráficas generadas por los notebooks
│
├── requirements.txt
├── .gitignore
├── README.md
└── CLAUDE.md                       ← Contexto completo del proyecto para agentes de IA
```

---

## Requisitos previos

- **OS**: Debian 12 Bookworm (Linux) — también compatible con cualquier Debian/Ubuntu reciente
- **Python**: 3.11 o superior (`python3 --version`)
- **pip**: incluido con Python 3.11
- **Git**: para clonar el repositorio

---

## Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/ML-for-Insurance.git
cd ML-for-Insurance
```

### 2. Crear y activar el entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

> Para desactivar el entorno: `deactivate`

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verificar la instalación

```bash
python -c "import chainladder, pygam, shap; print('OK — dependencias cargadas')"
```

### 5. Ejecutar los tests

```bash
pytest tests/ -v
```

### 6. Lanzar Jupyter

```bash
jupyter notebook notebooks/
```

---

## Flujo de trabajo recomendado

```
01_exploracion  →  02_actuarial  →  03_rcs_var
                                         ↓
                              04_ml_interpretable
                                         ↓
                                    05_hibrido
                                         ↓
                                   06_validacion
```

Cada carpeta de notebooks contiene un `README.md` local con el objetivo del sprint y los entregables esperados.

---

## Datos

Los datos de siniestros provienen del **portal oficial de la CNSF**:

```
https://www.cnsf.gob.mx/EntidadesSupervisadas/InstitucionesSociedadesMutualistas/
Paginas/DetalladaSeguros.aspx
```

Ramos disponibles: Vida · Accidentes y Enfermedades · Automóviles

Los archivos descargados se colocan en `data/raw/` y **no se versionan** (ver `.gitignore`). El script de descarga se encuentra en `src/data_io/loader.py`.

---

## Documentación técnica de referencia

| Documento | Descripción |
|---|---|
| `docs/Modelos_Reserva_CUSF.pdf` | Metodologías aceptadas por la CUSF y obstáculos para ML de caja negra |
| `docs/Requerimiento_Capital_Solvencia_CUSF.pdf` | Presentación ejecutiva del RCS y la Fórmula General |
| `docs/notas_tecnicas/` | Notas metodológicas generadas durante el proyecto |

---

## Estado del proyecto

| Mes | Sprint | Estado |
|---|---|---|
| 1 | Setup + EDA + Scraping CNSF | ⬜ Pendiente |
| 2 | Modelos actuariales estándar | ⬜ Pendiente |
| 3 | RCS Fórmula General + VaR 99.5 % | ⬜ Pendiente |
| 4 | ML interpretable (GAMs, árboles) | ⬜ Pendiente |
| 5 | Arquitectura híbrida + SHAP global | ⬜ Pendiente |
| 6 | Validación + Memoria técnica final | ⬜ Pendiente |

---

## Licencia

MIT · Gabriel Fernando Rosas Zepeda · 2026
