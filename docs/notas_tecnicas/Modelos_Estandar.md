---
title: "Modelos Estándar de Reservas Técnicas"
subtitle: "Referencia práctica para el cálculo de reservas bajo la CUSF (México)"
author: "Gabriel Fernando Rosas Zepeda"
date: "2026"

# ── Motor y fuentes ────────────────────────────────────────────────
pdf-engine: xelatex
mainfont: "DejaVu Serif"
monofont: "DejaVu Sans Mono"
monofontoptions:
  - Scale=0.85

# ── Márgenes ───────────────────────────────────────────────────────
geometry:
  - top=2.5cm
  - bottom=2.5cm
  - left=3cm
  - right=3cm

# ── Interlineado y tamaño ──────────────────────────────────────────
fontsize: 11pt
linestretch: 1.3

# ── Bloques de código ──────────────────────────────────────────────
highlight-style: tango
listings: false

# ── Header/footer ──────────────────────────────────────────────────
header-includes:
  - \usepackage{fancyhdr}
  - \pagestyle{fancy}
  - \fancyhf{}
  - \fancyhead[L]{\small Modelos Estándar de Reservas · CUSF}
  - \fancyhead[R]{\small \thepage}
  - \fancyfoot[C]{\small CNSF · versión compulsada 07-10-2024}
  - \renewcommand{\headrulewidth}{0.4pt}
  - \renewcommand{\footrulewidth}{0.4pt}

  # Fondo gris claro para bloques de código
  - \usepackage{mdframed}
  - \usepackage{fvextra}
  - \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\{\}}
  - \surroundwithmdframed[backgroundcolor=gray!12,linewidth=0pt,innerleftmargin=8pt,innerrightmargin=8pt,innertopmargin=6pt,innerbottommargin=6pt]{Shaded}

  # Tablas legibles
  - \usepackage{booktabs}
  - \usepackage{longtable}
  - \usepackage{array}

  # Hyperlinks
  - \usepackage{hyperref}
  - \hypersetup{colorlinks=true, linkcolor=blue!60!black, urlcolor=blue!60!black}
---

# Modelos Estándar de Reservas Técnicas

> Referencia práctica para el cálculo de reservas bajo la CUSF (México)  
> Marco regulatorio: Circular Única de Seguros y Fianzas · CNSF · versión compulsada 07-10-2024  
> Módulo del proyecto: `src/actuarial/`

---

## Contexto regulatorio

Toda institución de seguros en México debe constituir una **Reserva Técnica**:

```
Reserva Técnica = BEL + MR
```

- **BEL** (Mejor Estimación): valor esperado de flujos futuros de obligaciones, descontado con la curva libre de riesgo publicada por la CNSF.
- **MR** (Margen de Riesgo): costo de capital del riesgo no diversificable, calculado sobre los RCS futuros con una tasa de ~10 %.

El componente central del BEL para siniestros es el **IBNR** (Incurred But Not Reported): lo que ya ocurrió pero aún no se ha pagado ni reportado completamente. Los cinco modelos de esta referencia calculan o cuantifican el IBNR.

---

## Insumo común: el triángulo de desarrollo

Todos los modelos parten del mismo insumo: un **triángulo de pagos acumulados**.

```
              Año de desarrollo
              1       2       3       4
Año   2021    100     150     165     170
de    2022    120     180     198
orig. 2023    140     200
      2024    160
```

- **Filas**: año en que ocurrió el siniestro (año de origen).
- **Columnas**: cuántos años han pasado desde que ocurrió (año de desarrollo).
- **Celda**: pagos acumulados hasta ese momento.
- **Diagonal inferior**: datos conocidos hoy.
- **Triángulo inferior vacío**: lo que los modelos deben proyectar.

---

## 1. Chain Ladder — Estimación base

**¿Cuándo usarlo?** Cuando los datos históricos son suficientes y estables, y se confía en que el pasado representa bien el futuro.

### Idea central

Calcular cuánto crecen los pagos de un año de desarrollo al siguiente (factores de desarrollo o *link-ratios*), y aplicar esos factores a las diagonales incompletas del triángulo.

### Algoritmo paso a paso

**Paso 1 — Calcular los factores de desarrollo:**

```
f_j = Σ C(i, j+1) / Σ C(i, j)
```

donde `C(i, j)` es el pago acumulado del año de origen `i` en el año de desarrollo `j`.

**Paso 2 — Proyectar el triángulo:**

Multiplicar cada diagonal incompleta por los factores correspondientes hasta llegar al año de desarrollo final (cola).

**Paso 3 — Calcular el IBNR:**

```
IBNR(i) = C(i, último desarrollo proyectado) - C(i, último desarrollo conocido)
IBNR total = Σ IBNR(i)
```

### Supuesto crítico

Los factores de desarrollo son estables en el tiempo. Si hay cambios estructurales en el negocio (inflación de siniestros, cambios legales, pandemia), Chain Ladder los absorbe sin distinguirlos.

### En el proyecto

```python
# src/actuarial/chain_ladder.py
import chainladder as cl
triangle = cl.Triangle(data, ...)
model = cl.Chainladder().fit(triangle)
ibnr = model.ibnr_
```

---

## 2. Bornhuetter-Ferguson — Estimación con juicio

**¿Cuándo usarlo?** Cuando los datos son escasos, inestables, o el año de origen es reciente y tiene poca experiencia propia. Combina datos observados con una estimación a priori del negocio.

### Idea central

En lugar de confiar 100 % en los factores históricos (como CL), BF pondera la experiencia real con una **pérdida última esperada a priori** (derivada de primas, índices de siniestralidad del mercado, o juicio actuarial).

### Algoritmo paso a paso

**Paso 1 — Obtener los factores de desarrollo** (igual que Chain Ladder).

**Paso 2 — Calcular el porcentaje no desarrollado:**

```
q(j) = 1 - 1 / f(j → último)
```

Es la fracción del IBNR que aún falta por desarrollarse en el año de desarrollo `j`.

**Paso 3 — Definir la pérdida última a priori:**

```
ELR (Expected Loss Ratio) × Prima devengada = Pérdida última esperada a priori
```

**Paso 4 — Calcular el IBNR BF:**

```
IBNR_BF(i) = Pérdida última a priori(i) × q(j_actual(i))
```

**Paso 5 — Pérdida última BF:**

```
Pérdida última BF(i) = C(i, j_actual) + IBNR_BF(i)
```

### Supuesto crítico

La estimación a priori es razonable. Si el ELR está mal calibrado, BF hereda ese error. Para carteras maduras con buena historia, CL suele ser preferible; para carteras jóvenes, BF es más estable.

### En el proyecto

```python
# src/actuarial/bornhuetter_ferguson.py
model = cl.BornhuetterFerguson(apriori=0.65).fit(triangle)
ibnr = model.ibnr_
```

---

## 3. Cape Cod — Equilibrio entre datos y negocio

**¿Cuándo usarlo?** Cuando se quiere una estimación más estable que Chain Ladder pero sin necesidad de definir un ELR externo como en BF. El propio dato histórico calibra la pérdida esperada.

### Idea central

Es una variante de BF donde el ELR **no se define externamente**, sino que se estima directamente desde la experiencia histórica del ramo y la prima devengada. Equilibra la información del portafolio con el tamaño del negocio.

### Algoritmo paso a paso

**Paso 1 — Calcular los factores de desarrollo** (igual que CL).

**Paso 2 — Estimar el ELR implícito desde los datos:**

```
ELR_CapeCode = Σ C(i, j_actual) / Σ [Prima(i) × (1 - q(j_actual(i)))]
```

donde el denominador es la prima ajustada por el porcentaje ya desarrollado (prima "usada").

**Paso 3 — Aplicar como BF** con ese ELR calibrado internamente:

```
IBNR_CC(i) = ELR_CapeCode × Prima(i) × q(j_actual(i))
```

### Diferencia clave con BF

| | Bornhuetter-Ferguson | Cape Cod |
|---|---|---|
| ELR | Definido externamente por el actuario | Calibrado desde los propios datos |
| Dependencia de juicio | Alta | Media |
| Estabilidad | Alta cuando el juicio es bueno | Alta cuando los datos son representativos |

### En el proyecto

```python
# src/actuarial/cape_cod.py
model = cl.CapeCod().fit(triangle)
ibnr = model.ibnr_
```

---

## 4. Mack — Cuantificación de incertidumbre

**¿Cuándo usarlo?** Cuando se necesita no solo la estimación del IBNR sino también su **incertidumbre**, para cumplir con los requisitos de intervalos de confianza del BEL que exige la CUSF.

### Idea central

Mack es una extensión estocástica de Chain Ladder. Mantiene exactamente la misma estimación puntual del IBNR, pero añade una capa estadística que calcula la **varianza** y los **intervalos de confianza** sin asumir una distribución paramétrica específica.

### Lo que calcula Mack

**Estimación puntual:** idéntica a Chain Ladder.

**Error estándar del IBNR:**

```
se(IBNR(i)) = función de los factores de desarrollo y su variabilidad histórica
```

**Intervalo de confianza aproximado (95 %):**

```
IC_95%(IBNR total) = IBNR ± 1.96 × se(IBNR total)
```

**Coeficiente de variación:**

```
CV = se(IBNR) / IBNR     ← indicador de qué tan incierta es la reserva
```

### Supuestos del modelo de Mack

1. Los factores de desarrollo de distintos años de origen son independientes.
2. La varianza de los pagos es proporcional a los pagos acumulados del período anterior (supuesto de varianza).
3. Los factores de desarrollo son estables (mismo supuesto que CL).

### Relevancia regulatoria (CUSF)

La CUSF solicita explícitamente el cálculo de intervalos de confianza para el Mejor Estimador. Mack es la herramienta de cumplimiento directo para ese requisito.

### En el proyecto

```python
# src/actuarial/mack.py
model = cl.MackChainladder().fit(triangle)
mse   = model.total_mse_          # error cuadrático medio total
se    = model.total_process_risk_  # error estándar
summary = model.summary_           # tabla completa por año de origen
```

---

## 5. Bootstrap — Simulación de escenarios

**¿Cuándo usarlo?** Cuando se necesita la **distribución completa** de posibles resultados del IBNR (no solo la media y el IC), para calcular el VaR al 99.5 % que exige el RCS.

### Idea central

En lugar de calcular la varianza analíticamente (como Mack), Bootstrap genera miles de triángulos sintéticos mediante **remuestreo de los residuos de Chain Ladder**, y aplica CL a cada uno. El resultado es una distribución empírica del IBNR.

### Algoritmo paso a paso

**Paso 1 — Ajustar Chain Ladder** al triángulo original y calcular los **residuos de Pearson**:

```
r(i,j) = [C(i,j) - C_ajustado(i,j)] / sqrt(C_ajustado(i,j))
```

**Paso 2 — Remuestrear los residuos** con reemplazo para construir un triángulo sintético.

**Paso 3 — Aplicar Chain Ladder** al triángulo sintético → obtener un IBNR simulado.

**Paso 4 — Repetir** N veces (mínimo 10,000 iteraciones para estabilidad del percentil 99.5 %).

**Paso 5 — Construir la distribución empírica** del IBNR y extraer percentiles:

```
P50  → mediana del IBNR
P75  → reserva conservadora
P95  → reserva para gestión de riesgo
P99.5 → umbral RCS (requisito CUSF)
```

### Relación con el RCS

```
VaR 99.5% = percentil 99.5 de la distribución Bootstrap del IBNR total
RCS (componente técnico) ≈ VaR 99.5% - BEL (media de la distribución)
```

### En el proyecto

```python
# src/actuarial/bootstrap.py
model = cl.BootstrapODPSample(n_sims=10_000, random_state=42).fit(triangle)
ibnr_dist = model.ibnr_.to_frame()   # distribución completa
p995 = ibnr_dist.quantile(0.995)     # VaR para el RCS
```

---

## Tabla comparativa

| Modelo | Salida principal | Incertidumbre | Juicio actuarial | Uso principal en CUSF |
|---|---|---|---|---|
| Chain Ladder | IBNR puntual | No | Mínimo | Estimación base obligatoria |
| Bornhuetter-Ferguson | IBNR puntual | No | Alto (ELR externo) | Carteras jóvenes o inestables |
| Cape Cod | IBNR puntual | No | Medio (ELR calibrado) | Alternativa estable a CL |
| Mack | IBNR + IC + varianza | Analítica | Mínimo | Cumplimiento IC del BEL (CUSF) |
| Bootstrap | Distribución completa | Empírica (simulación) | Mínimo | VaR 99.5 % para el RCS |

---

## Flujo de uso recomendado en el proyecto

```
Triángulo de desarrollo (data/processed/)
        │
        ├── Chain Ladder     → IBNR base (benchmark)
        ├── BF / Cape Cod    → IBNR con juicio / estabilizado
        ├── Mack             → IC del BEL para reporte regulatorio
        └── Bootstrap        → Distribución completa → VaR 99.5 % → RCS
```

Para la comparación con modelos ML (Sprint 4 y 5), el **IBNR de Chain Ladder** es el target de referencia y el **percentil 99.5 % de Bootstrap** es el umbral que cualquier modelo alternativo debe reproducir o superar.

---

## Referencias

- Circular Única de Seguros y Fianzas (CUSF) · Capítulos 5, 6 y 8 · CNSF · versión compulsada 07-10-2024
- Mack, T. (1993). *Distribution-free calculation of the standard error of chain ladder reserve estimates*. ASTIN Bulletin.
- England, P. & Verrall, R. (2002). *Stochastic claims reserving in general insurance*. British Actuarial Journal.
- Librería `chainladder` (Python): https://chainladder-python.readthedocs.io
