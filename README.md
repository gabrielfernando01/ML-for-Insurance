<p align="center">
  <img src=".github/logo.png" width="90" alt="Escudo UNAM"/>
</p>

<p align="center">
  <img src=".github/cover.svg" width="100%" alt="ML para Pricing en Aseguradoras"/>
</p>

---

# ML-for-Insurance

Investigación sobre capacidad predictiva en pricing de Seguro de Vida Individual:  
**¿cuánta ganancia aporta Machine Learning moderno sobre GLM, y a qué costo de interpretabilidad?**

Datos públicos de la Comisión Nacional de Seguros y Fianzas (CNSF), período 2021–2024.

---

## Contexto y motivación

La CNSF publica anualmente estadísticas de operación del mercado asegurador mexicano.
Los datos de `Vida Individual` no individualizan registros por razones de confidencialidad,
pero comparten seis campos comunes entre las tres tablas (`emision`, `siniestros`, `comisiones`),
lo que permite **inducir cohortes** y construir métricas de siniestralidad, frecuencia y
severidad por segmento demográfico y geográfico.

El trabajo se articula en dos capas de modelado:

| Capa | Método | Rol |
|---|---|---|
| Baseline | GLM (Poisson / Gamma / Tweedie) | Estándar de la industria actuarial |
| Challenger | ML moderno (XGBoost / LightGBM) | Capacidad predictiva incremental |

La comparación no es técnica por sí sola — el resultado de interés es la **frontera
interpretabilidad / desempeño** y su implicación regulatoria.

---

## Datos

| Tabla | Archivo origen | Filas (2021–2024) | Columnas |
|---|---|---|---|
| `emision` | Hoja `emision` por año | 3,508,593 | 12 |
| `siniestros` | Hoja `siniestros` por año | 297,505 | 13 |
| `comisiones` | Hoja `comisiones` por año | 827,907 | 16 |

**Campos compartidos (candidatos a clave de cohorte):**  
`ANIO`, `ENTIDAD`, `SEXO`, `EDAD`, `COBERTURA`, `PLAN_DE_LA_POLIZA`

---

## Estructura del proyecto

```
ML-for-Insurance/
│
├── data/
│   ├── raw/                        # Excels originales CNSF (no versionados)
│   │   ├── 2021 Vida Individual Bases.xlsx
│   │   ├── 2022 Vida Individual Bases.xlsx
│   │   ├── 2023_Vida_Individual_Bases.xlsx
│   │   └── 2024_Vida_Individual_Bases.xlsx
│   ├── processed/                  # CSVs concatenados por tabla
│   │   ├── emision_total.csv
│   │   ├── siniestros_total.csv
│   │   └── comisiones_total.csv
│   └── prepared/                   # Parquet limpios — punto de entrada para análisis
│       ├── emision.parquet
│       ├── siniestros.parquet
│       └── comisiones.parquet
│
├── notebooks/
│   ├── extract/
│   │   ├── extract_data.ipynb      # Extracción de hojas Excel → CSV
│   │   └── rename_sheets.ipynb     # Normalización local de nombres de hoja
│   ├── prepare_datasets.ipynb      # ETL canónico: limpieza, casteo, exporta Parquet
│   └── main_data.ipynb             # Análisis, cohortes y modelado — parte desde Parquet
│
├── .gitignore
└── README.md
```

---

## Pipeline

```
raw/*.xlsx
    │
    ▼  extract_data.ipynb
processed/*_total.csv
    │
    ▼  prepare_datasets.ipynb
prepared/*.parquet
    │
    ▼  main_data.ipynb
cohortes → GLM → ML → comparación
```

Cada etapa es idempotente: se puede re-ejecutar sin afectar las etapas anteriores.

---

## Reproducibilidad

```bash
# 1. Instalar dependencias
pip install pandas numpy pyarrow scikit-learn lightgbm xgboost jupyter

# 2. Colocar los Excel originales en data/raw/

# 3. Ejecutar en orden
jupyter nbconvert --to notebook --execute notebooks/extract/extract_data.ipynb
jupyter nbconvert --to notebook --execute notebooks/prepare_datasets.ipynb
# A partir de aquí, main_data.ipynb es interactivo
```

---

## Estado actual

- [x] Extracción de fuentes CNSF 2021–2024
- [x] Limpieza y normalización de columnas
- [x] Casteo de tipos numéricos
- [x] Export a Parquet
- [ ] Construcción de cohortes por clave compuesta
- [ ] Modelo GLM baseline
- [ ] Modelo ML challenger
- [ ] Comparación interpretabilidad / desempeño

---

## Fuente de datos

Comisión Nacional de Seguros y Fianzas — Estadísticas de Seguros  
[InstitucionesSociedadesMutualistas](https://www.cnsf.gob.mx/EntidadesSupervisadas/InstitucionesSociedadesMutualistas/Paginas/DetalladaSeguros.aspx)  
Ramo: Vida Individual | Período: 2021–2024
