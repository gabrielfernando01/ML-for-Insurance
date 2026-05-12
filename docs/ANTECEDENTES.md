# Antecedentes — ML-for-Insurance

## Contexto del proyecto

El objetivo es explorar si es posible implementar modelos de machine learning para
**pricing de Seguro de Vida Individual** a partir de datos públicos agregados, sin
disponer de pólizas individualizadas.

Los datos provienen de la **Comisión Nacional de Seguros y Fianzas (CNSF)** y cubren
el periodo **2021–2024**. Se distribuyen en tres tablas temáticas:

| Tabla | Filas | Columnas | Descripción |
|---|---|---|---|
| `emision` | 3,508,593 | 12 | Prima emitida, suma asegurada, número de asegurados por segmento |
| `siniestros` | 297,505 | 13 | Siniestros reportados y montos pagados por segmento |
| `comisiones` | 827,907 | 16 | Comisiones pagadas a intermediarios por segmento |

Las tablas **no comparten un ID o foreign key explícito**. La correlación entre ellas
deberá inferirse por segmentación: `ANIO`, `ENTIDAD`, `SEXO`, `EDAD`, `COBERTURA`, y
variables similares disponibles en las tres fuentes.

---

## Lo que se ha hecho hasta ahora

### 1. Extracción (`extract_data.ipynb`)

Se leyeron los cuatro archivos Excel anuales del directorio `data/raw/`, iterando sobre
las hojas `emision`, `siniestros` y `comisiones`. A cada registro se le añadió la
columna `ANIO` y los frames resultantes se concatenaron y guardaron como CSV en
`data/processed/`.

### 2. Limpieza inicial (`data_cleaning.ipynb`)

Se realizaron transformaciones mínimas para dejar los datos utilizables:

- **Detección de encabezados embebidos** — los exports de CNSF repiten la fila de
  encabezado dentro de los datos cada cierto número de registros. Se aplicó una máscara
  con `df.isin(header_cols).any(axis=1)` para identificarlos. En este caso el resultado
  fue 0 filas eliminadas, confirmando que los CSVs concatenados ya venían limpios de
  ese patrón.

- **Promoción de encabezados reales** — la fila 0 de cada tabla contenía los nombres
  reales de columna (e.g. `EDAD`, `COBERTURA`, `ENTIDAD`). Se promovió como header y
  se eliminó de los datos con `df.iloc[1:].copy()`.

- **Guardado del punto de partida limpio** — los tres DataFrames resultantes se
  escribieron en `data/processed/clean/` como `emision_clean.csv`,
  `siniestros_clean.csv` y `comisiones_clean.csv`. Este directorio es el punto de
  partida para todo análisis posterior; los archivos `_total.csv` en `processed/` se
  conservan como respaldo de la extracción cruda.

No se han aplicado casteos de tipos, imputaciones, ni transformaciones de variables.

---

## Estado actual

Los archivos en `data/processed/clean/` están listos para inspección. El siguiente
paso es determinar:

1. Si los tipos, rangos y distribuciones de las columnas son coherentes con datos de
   seguros de vida.
2. Qué columnas comparten las tres tablas y si es posible construir una clave compuesta
   que permita cruzarlas.
3. Si la granularidad de los datos agregados es suficiente para construir features
   válidos para modelos de pricing (frecuencia, severidad, siniestralidad, prima por
   asegurado).

---

## Pregunta central del proyecto

> ¿Es posible entrenar modelos de ML para pricing de Seguro de Vida Individual
> a partir de datos públicos de la CNSF, sin acceso a pólizas individualizadas?

La hipótesis de trabajo es que sí, mediante inferencia por grupos demográficos y
geográficos, construyendo features agregados por segmento que aproximen la exposición
y el riesgo a nivel de cohorte.

---

## Estructura del proyecto

```
ML-for-Insurance/
├── data/
│   ├── raw/                        # Excel anuales CNSF (2021–2024)
│   ├── processed/
│   │   ├── *_total.csv             # Extracción cruda concatenada
│   │   └── clean/                  # Punto de partida limpio ← trabajar aquí
│   └── external/                   # Fuentes externas (tablas de mortalidad, etc.)
├── notebooks/
│   ├── extract_data.ipynb          # Lectura de xlsx y concatenación
│   ├── data_cleaning.ipynb         # Limpieza inicial y promoción de headers
│   └── rename_sheets.ipynb
├── docs/
│   └── ANTECEDENTES.md             # Este archivo
├── src/
│   ├── features/                   # Feature engineering
│   ├── models/                     # Entrenamiento y evaluación
│   └── viz/                        # Visualizaciones
├── reports/
├── logs/
└── requirements.txt
```

---

*Última actualización: mayo 2026*
