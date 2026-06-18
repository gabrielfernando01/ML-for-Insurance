# Inducción: Fundamentos Actuariales de Pricing con ML
### Proyecto ML-for-Insurance · Vida Individual CNSF 2021–2024

> **Para quién es este documento:** Actuario con formación en teoría del riesgo  
> que quiere entender cómo esos fundamentos se materializan en un modelo de  
> tarificación real y cómo ML entra en ese flujo.

---

## 0. El puente que nadie explica en la licenciatura

En teoría del riesgo aprendes:

$$S = \sum_{j=1}^{N} Y_j \qquad E[S] = E[N] \cdot E[Y]$$

En pricing actuarial te dicen:

$$\text{Prima Pura} = \text{Frecuencia} \times \text{Severidad}$$

**Son exactamente lo mismo.** La licenciatura te da el fundamento probabilístico; el pricing te da el flujo operativo. Este documento construye ese puente de manera explícita.

---

## 1. ¿Modelo individual o colectivo? — El caso de tus datos CNSF

### La pregunta correcta

Los datos CNSF de Vida Individual no individualizan pólizas por confidencialidad. Lo que tienes son **cohortes**: grupos de asegurados con el mismo `(ANIO, ENTIDAD, SEXO, EDAD, COBERTURA, PLAN_DE_LA_POLIZA)`.

Dentro de cada cohorte observas:
- cuántos asegurados hay (expuestos)
- cuántos siniestros ocurrieron (frecuencia agregada)
- cuánto se pagó en total (severidad agregada)

Esto es el **modelo colectivo**:

$$S_{\text{cohorte}} = \sum_{j=1}^{N_{\text{cohorte}}} Y_j$$

donde $N_{\text{cohorte}}$ es el número de siniestros de esa cohorte e $Y_j$ el monto del siniestro $j$.

### ¿Por qué no es modelo individual?

El modelo individual requiere conocer $q_j$ (probabilidad de reclamación) y $C_j$ (monto potencial) **por póliza**. Con datos CNSF públicos no tienes resolución individual — tienes comportamiento agregado por segmento. La estructura es:

```
Cohorte (EDAD=35, SEXO=M, ENTIDAD=09, PLAN=A)
    ├── Expuestos:    1,240 pólizas-año
    ├── Siniestros:   18 eventos
    └── Monto total:  $4,320,000
```

El modelo individual vive en el nivel de la fila de póliza; el modelo colectivo en el nivel de la cohorte. **Tus datos son cohortes → modelo colectivo.**

### Implicación práctica

Esto no es una limitación — es la realidad del 90% del pricing actuarial. Las aseguradoras tampoco modelan póliza a póliza en la mayoría de los ramos; modelan segmentos. La ganancia de ML sobre GLM en tu proyecto se medirá en precisión de la estimación por cohorte.

---

## 2. De la teoría del riesgo al GLM: el mapa completo

### 2.1 La identidad fundamental

$$\underbrace{E[S]}_{\text{prima pura total}} = \underbrace{E[N]}_{\text{frecuencia esperada}} \times \underbrace{E[Y]}_{\text{severidad esperada}}$$

Esta igualdad (Proposición 1.5 del modelo colectivo) **es** la descomposición Frecuencia × Severidad del pricing. No son conceptos distintos; son el mismo resultado con distinto vocabulario.

| Teoría del riesgo | Pricing actuarial | Tu dataset CNSF |
|---|---|---|
| $N$ — número de siniestros | Frecuencia bruta | `siniestros / expuestos` |
| $Y_j$ — monto del siniestro $j$ | Severidad individual | `monto_total / siniestros` |
| $E[N] / \text{Expuestos}$ | Tasa de siniestralidad | Feature objetivo del GLM de frecuencia |
| $E[Y \mid N > 0]$ | Severidad media | Feature objetivo del GLM de severidad |
| $E[S] / \text{Expuestos}$ | Loss cost (costo puro por asegurado) | Producto final: frecuencia × severidad |

### 2.2 ¿Dónde vive Esscher, utilidad y credibilidad en este flujo?

Estas herramientas **no son el motor del GLM**; son la justificación y el ajuste de sus resultados. El mapa es:

```
TEORÍA DEL RIESGO                    PRICING OPERATIVO
─────────────────                    ─────────────────

E[S] = E[N]·E[Y]         →          Prima Pura = Frec × Sev
                                              ↑
                                          GLM estima esto

Principio de Esscher       →          Ajuste de cola / recargo técnico
(distorsión conservadora                para riesgos catastróficos
 de la distribución)

Utilidad cero / valor medio →         Margen de utilidad
(p⁻ ≤ p ≤ p⁺)                        (negotiation band entre
                                       asegurador y mercado)

Teoría de la credibilidad  →          Blending de experiencia propia
Z·x̄ + (1-Z)·μ                        vs. tabla de la industria
(cuando datos propios son              (muy relevante en tu caso:
 escasos por cohorte)                  cohortes con pocos siniestros)
```

**Conclusión:** Para construir el GLM, necesitas principalmente entender la descomposición Frecuencia × Severidad y las distribuciones correctas. Esscher y utilidad son recargos que vienen **después** del GLM.

---

## 3. El GLM actuarial: estructura completa

### 3.1 Por qué se usa GLM y no regresión lineal

El riesgo $S$ tiene dos propiedades que violan los supuestos de OLS:

1. **Asimetría:** la distribución de siniestros tiene cola derecha pesada (pocos eventos grandes)
2. **Heteroscedasticidad estructural:** la varianza depende de la media (en Poisson, $\text{Var}[N] = E[N]$)

El GLM resuelve esto con:
- una **distribución** de la familia exponencial que captura la asimetría correcta
- una **función de enlace** que lineariza la relación entre predictores y respuesta

### 3.2 Dos modelos, no uno

En la práctica se ajustan **dos GLMs separados**, uno por componente:

#### Modelo de Frecuencia

$$\ln\!\left(\frac{E[N_i]}{e_i}\right) = \beta_0 + \beta_1 x_1 + \cdots + \beta_k x_k$$

donde $e_i$ son los **expuestos** (pólizas-año) de la cohorte $i$.

Equivalentemente, usando el offset:

$$\ln(E[N_i]) = \ln(e_i) + \beta_0 + \beta_1 x_1 + \cdots + \beta_k x_k$$

| Componente | Elección estándar | Alternativa |
|---|---|---|
| Distribución $N$ | Poisson | Binomial Negativa (sobredispersión) |
| Función de enlace | Log | — |
| Variable respuesta | Número de siniestros | — |
| Offset obligatorio | $\ln(\text{expuestos})$ | — |

> **Offset:** sin él, una cohorte de 10,000 expuestos y otra de 100 con el mismo  
> número de siniestros parecerían igualmente "frecuentes". El offset corrige esto  
> dividiendo implícitamente por exposición.

#### Modelo de Severidad

$$\ln(E[Y_i]) = \beta_0 + \beta_1 x_1 + \cdots + \beta_k x_k$$

| Componente | Elección estándar | Alternativa |
|---|---|---|
| Distribución $Y$ | Gamma | Log-Normal, Burr |
| Función de enlace | Log (inversa canónica) | — |
| Variable respuesta | Monto promedio por siniestro | — |
| Peso | Número de siniestros | — |
| Offset | No aplica (ya es promedio) | — |

> **Peso:** ponderar por número de siniestros da más peso a cohortes con más  
> observaciones, lo cual es correcto estadísticamente.

#### Por qué log-link en ambos

Con enlace log, el modelo es **multiplicativo**:

$$E[Y] = e^{\beta_0} \cdot e^{\beta_1 x_1} \cdot e^{\beta_2 x_2} \cdots$$

Esto es natural en seguros: el efecto de tener 35 años *en lugar de* 25 es un **multiplicador** sobre la prima base, no una suma. Los tarifarios de las aseguradoras se expresan precisamente como factores multiplicativos (relatividades).

### 3.3 De coeficientes a relatividades

El resultado del GLM no se presenta como $\hat{\beta}_i$ — se presenta como **relatividades**:

$$\text{Relatividad}(x_i = k) = \frac{e^{\hat{\beta}_0 + \hat{\beta}_k}}{e^{\hat{\beta}_0}} = e^{\hat{\beta}_k}$$

Ejemplo real: si el GLM estima $\hat{\beta}_{\text{SEXO=F}} = -0.15$, la relatividad es $e^{-0.15} \approx 0.86$, es decir, las mujeres tienen un 14% menos frecuencia que el grupo base, *ceteris paribus*.

### 3.4 El modelo de doble distribución (Tweedie)

Existe un atajo: el modelo Tweedie modela directamente el **loss cost** ($\text{Frecuencia} \times \text{Severidad}$) con una sola distribución que mezcla masa en cero (sin siniestro) con cola continua positiva (con siniestro).

$$Y_{\text{Tweedie}} \sim \text{Tweedie}(\mu, \phi, p), \quad 1 < p < 2$$

La ventaja es simplicidad. La desventaja es que no separa los efectos sobre frecuencia y severidad — información valiosa para el pricing. **Para tu proyecto, los modelos separados son más informativos.**

---

## 4. Variables de tarificación: de los campos CNSF a los features del modelo

### 4.1 Lo que tienes vs. lo que necesitas

| Campo CNSF | Rol en pricing | Tipo de feature |
|---|---|---|
| `EDAD` | Principal driver de mortalidad/siniestralidad | Continuo → transformar o spline |
| `SEXO` | Factor demográfico de riesgo | Categórico binario |
| `ENTIDAD` | Proxy de acceso a salud, nivel socioeconómico | Categórico (32 niveles) |
| `COBERTURA` | Define qué riesgos cubre la póliza | Categórico |
| `PLAN_DE_LA_POLIZA` | Estructura del producto (temporal, dotal, etc.) | Categórico |
| `ANIO` | Tendencia temporal, inflación médica | Numérico o dummy |

### 4.2 Construcción de las variables respuesta por cohorte

Para cada cohorte única `(ANIO, ENTIDAD, SEXO, EDAD, COBERTURA, PLAN)`:

```python
# Desde emision.parquet + siniestros.parquet

cohorte = (
    emision.groupby(clave_cohorte)
    .agg(expuestos=('NUM_POLIZAS', 'sum'))          # o suma de años-póliza
    .join(
        siniestros.groupby(clave_cohorte).agg(
            n_siniestros=('NUM_SINIESTROS', 'sum'),
            monto_total=('MONTO_PAGADO', 'sum')
        )
    )
    .fillna({'n_siniestros': 0, 'monto_total': 0})
)

# Variables respuesta
cohorte['frecuencia']   = cohorte['n_siniestros'] / cohorte['expuestos']
cohorte['severidad']    = cohorte['monto_total'] / cohorte['n_siniestros']  # solo donde n > 0
cohorte['loss_cost']    = cohorte['monto_total'] / cohorte['expuestos']
```

### 4.3 Transformación de la edad

La edad no entra lineal al modelo log: la mortalidad sigue una curva (Makeham-Gompertz). Opciones:

```python
# Opción 1: Spline cúbico natural (recomendado para GLM)
from patsy import cr
edad_spline = cr(cohorte['EDAD'], df=4)

# Opción 2: Polinomio (más simple, menos flexible)
cohorte['EDAD_2'] = cohorte['EDAD'] ** 2

# Opción 3: Bandas (muy usado en tarifarios)
cohorte['BANDA_EDAD'] = pd.cut(cohorte['EDAD'],
    bins=[0, 25, 35, 45, 55, 65, 100],
    labels=['<25','25-35','35-45','45-55','55-65','65+'])
```

### 4.4 El problema de cohortes ralas (*sparse cohorts*)

Algunas combinaciones `(EDAD=72, PLAN=X, ENTIDAD=Colima)` tendrán muy pocos expuestos — quizás 0 siniestros en 4 años. Aquí entra la **teoría de la credibilidad**:

$$\hat{\mu}_{\text{cohorte}} = Z \cdot \bar{x}_{\text{cohorte}} + (1 - Z) \cdot \mu_{\text{global}}$$

donde $Z = n / (n + k)$ y $k$ es el parámetro de credibilidad (estimado por ANOVA o Bühlmann). En la práctica, el GLM con regularización (Ridge/Lasso) hace algo equivalente automáticamente.

---

## 5. El flujo completo de pricing: de datos a prima técnica

```
DATOS CNSF
(emision + siniestros + comisiones)
          │
          ▼
    CONSTRUCCIÓN DE COHORTES
    (clave 6 campos, variables respuesta)
          │
          ▼
   ┌──────┴──────┐
   │             │
   ▼             ▼
GLM FRECUENCIA  GLM SEVERIDAD
Poisson + log   Gamma + log
offset: ln(exp) peso: n_siniestros
   │             │
   ▼             ▼
 Ê[N/e]       Ê[Y|N>0]
   │             │
   └──────┬──────┘
          │  ×
          ▼
    LOSS COST PURO
    E[S] / Expuestos
          │
          ▼
    + RECARGOS TÉCNICOS          ← aquí entra Esscher / percentil de cola
    (gastos, utilidad, margen)   ← aquí entra utilidad cero / principio del %
          │
          ▼
    PRIMA TÉCNICA
    Prima Pura + Gastos + Margen
```

### ¿Dónde entra ML en este flujo?

ML (XGBoost / LightGBM) reemplaza o aumenta el bloque de estimación:

```
GLM FRECUENCIA  →  reemplazar por  →  LightGBM (frecuencia)
GLM SEVERIDAD   →  reemplazar por  →  LightGBM (severidad)
```

Los recargos técnicos y la estructura de prima técnica **permanecen iguales** — ML solo mejora la estimación de Frecuencia × Severidad. Eso es exactamente lo que quieres medir.

---

## 6. La frontera interpretabilidad / desempeño

Esta es la pregunta de investigación central del proyecto. Aquí está el marco completo:

### 6.1 Lo que el GLM da por diseño

| Atributo | GLM | ML (XGBoost/LightGBM) |
|---|---|---|
| Coeficientes interpretables | ✓ | ✗ directamente |
| Relatividades por variable | ✓ (directo) | Con SHAP |
| Aprobación regulatoria CNSF | ✓ establecido | ✗ en proceso / riesgo |
| Captura interacciones | Parcial (manual) | ✓ automática |
| Captura no-linealidades | Parcial (transformaciones) | ✓ automática |
| Requiere feature engineering | Significativo | Menor |
| Sobreajuste en cohortes ralas | Bajo (regularización implícita) | Alto sin tuning |

### 6.2 Métricas de comparación

Para frecuencia (Poisson):
```python
# Deviance de Poisson (métrica correcta, no RMSE)
from sklearn.metrics import mean_poisson_deviance
d_glm = mean_poisson_deviance(y_true, y_pred_glm, sample_weight=expuestos)
d_ml  = mean_poisson_deviance(y_true, y_pred_ml,  sample_weight=expuestos)
mejora = (d_glm - d_ml) / d_glm  # ganancia porcentual de ML
```

Para severidad (Gamma):
```python
from sklearn.metrics import mean_gamma_deviance
d_glm = mean_gamma_deviance(y_true, y_pred_glm, sample_weight=n_siniestros)
d_ml  = mean_gamma_deviance(y_true, y_pred_ml,  sample_weight=n_siniestros)
```

Loss ratio test (validación económica):
```python
# El modelo bien calibrado debe cumplir E[S_real / S_predicho] ≈ 1 por decil
cohorte['ratio'] = cohorte['monto_real'] / cohorte['prima_pura_estimada']
cohorte.groupby(pd.qcut(cohorte['prima_pura_estimada'], 10))['ratio'].mean()
# Un buen modelo tiene esta columna cercana a 1 en todos los deciles
```

### 6.3 Interpretabilidad de ML con SHAP

```python
import shap

explainer = shap.TreeExplainer(modelo_lgbm)
shap_values = explainer.shap_values(X_test)

# Equivalente a relatividades del GLM
shap.summary_plot(shap_values, X_test)

# Para una cohorte específica
shap.waterfall_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])
```

SHAP permite traducir el ML a un lenguaje que el regulador puede auditar.

---

## 7. Roadmap de implementación para tu proyecto

### Fase 1 — Cohortes (pendiente en README)
```
[ ] Unir emision + siniestros por clave de 6 campos
[ ] Calcular: expuestos, n_siniestros, monto_total por cohorte
[ ] Derivar: frecuencia, severidad, loss_cost
[ ] Diagnóstico: distribución de expuestos por cohorte (identificar ralas)
[ ] Separar train (2021–2022) / validation (2023) / test (2024)
```

### Fase 2 — GLM Baseline
```
[ ] GLM Frecuencia: Poisson + log + offset
    Variables: EDAD (spline), SEXO, ENTIDAD, COBERTURA, PLAN
[ ] GLM Severidad: Gamma + log + pesos
    Variables: mismas (los coeficientes serán distintos)
[ ] Loss cost = pred_frecuencia × pred_severidad
[ ] Diagnóstico: deviance plots, Q-Q residuales, lift curves por decil
[ ] Extraer relatividades → tabla de tarifas implícita
```

### Fase 3 — ML Challenger
```
[ ] LightGBM Frecuencia: objetivo poisson, con offset
    tweak: lgbm no tiene offset nativo → incluir ln(expuestos) como feature
[ ] LightGBM Severidad: objetivo gamma (o tweedie con p=1.5 para loss cost directo)
[ ] Tuning: CV temporal (no aleatorio — respeta el orden del tiempo)
[ ] SHAP: importancia global + relatividades implícitas
```

### Fase 4 — Comparación
```
[ ] Métricas: Poisson deviance, Gamma deviance, Gini, lift curves
[ ] Test de calibración: ratio E[real]/E[predicho] por decil de prima
[ ] Análisis de cohortes donde ML gana vs. pierde al GLM
[ ] Discusión regulatoria: ¿qué necesitaría la CNSF para aprobar ML?
```

---

## 8. Puntos de conexión teoría → práctica que debes tener claros

| Concepto de licenciatura | Materialización en el proyecto |
|---|---|
| $E[S] = E[N] \cdot E[Y]$ | Dos GLMs separados, multiplicados |
| Modelo colectivo Poisson compuesto | GLM de frecuencia con distribución Poisson |
| Distribución Gamma de severidades | GLM de severidad con distribución Gamma |
| Condición de ganancia neta $p > E(S)$ | Loading de gastos + margen encima del loss cost |
| Credibilidad de Bühlmann | Regularización del GLM / prior bayesiano en ML |
| Principio de Esscher | Recargo de cola para coberturas catastróficas |
| Principio del porcentaje | VaR del loss cost → prima de escenario extremo |
| Relatividades del GLM | $e^{\hat{\beta}_i}$ → factores del tarifario comercial |

---

## 9. Lecturas recomendadas para cerrar brechas

| Tema | Recurso |
|---|---|
| GLM actuarial completo | Frees, *Regression Modeling with Actuarial Applications* (2010) |
| Pricing con ML | Noll, Salzmann, Wüthrich — *Case Study: French Motor Third-Party Liability* (2020, SSRN) |
| SHAP en seguros | Lundberg & Lee — *A Unified Approach to Interpreting Model Predictions* (NeurIPS 2017) |
| Credibilidad | Bühlmann & Gisler — *A Course in Credibility Theory* (2005) |
| Datos CNSF | Metodología de estadísticas CNSF, Circular S-18.3 |

---

*Documento generado para el proyecto ML-for-Insurance | Vida Individual CNSF 2021–2024*
