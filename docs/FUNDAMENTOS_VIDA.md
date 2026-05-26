<p align="center">
  <img src="../.github/cover00.png" alt="ML para Pricing en Aseguradoras" width="98%"/>
</p>

# FUNDAMENTOS DE PRICING ACTUARIAL — VIDA INDIVIDUAL
### Referencia conceptual para `ML-for-Insurance`

---

## 1. Lo que pasa en la realidad: el ciclo del pricing

El ciclo actuarial de pricing no es un cálculo que ocurre una sola vez. Es iterativo:

```
┌─────────────────────────────────────────────────────────────────┐
│  1. TARIFICACIÓN                                                │
│     El actuario calcula la prima al inicio del período.         │
│     Usa tablas de mortalidad, tasas de interés, gastos          │
│     esperados y utilidad objetivo.                              │
│                                                                 │
│  2. EMISIÓN Y VIGENCIA                                          │
│     Las pólizas se emiten. La prima se cobra (en un pago        │
│     o en fraccionamientos periódicos).                          │
│                                                                 │
│  3. CIERRE DEL PERÍODO                                          │
│     La compañía observa siniestros reales y los contrasta       │
│     contra los esperados. Esto se llama estudio de experiencia. │
│                                                                 │
│  4. RETROALIMENTACIÓN                                           │
│     Si la experiencia difiere significativamente de lo          │
│     esperado, se recalibra la tarifa para el siguiente          │
│     período.                                                    │
└─────────────────────────────────────────────────────────────────┘
```

El contraste "¿fue suficiente la prima cobrada?" se refleja en el **estado de resultados** como la razón siniestral (*loss ratio*):

$$\text{Loss Ratio} = \frac{\text{Siniestros pagados + reservas}}{\text{Prima devengada}}$$

Un loss ratio < 1 no garantiza rentabilidad (aún faltan gastos y costo de capital), pero es la primera señal de que el pricing fue razonable.

**Punto de partida para tu proyecto**: las tablas `emision`, `siniestros` y `comisiones` de la CNSF son exactamente el reflejo de este ciclo — capturan los tres componentes que el actuario necesita para hacer ese contraste a nivel de cohorte.

---

## 2. Anatomía de la prima: de lo puro a lo comercial

La confusión de notación es legítima porque coexisten tres tradiciones: la actuarial clásica (vida), la de riesgo colectivo y la de pricing moderno. Aquí la jerarquía:

### 2.1 Prima neta o pura

Es el costo esperado del siniestro, sin ningún cargamento. Es el **piso matemático** de la prima: una compañía que cobre menos que esto esperaría perder dinero en valor esperado.

$$\Pi^{\text{neta}} = \mathbb{E}[S]$$

donde $S$ es el costo agregado de siniestros (definido en la sección 3).

**Notación $\Pi_x$**: es la notación de la actuaría clásica de vida para la **prima anual neta** de una póliza sobre una vida de edad $x$. Surge de la condición de equivalencia actuarial:

$$\Pi_x \cdot \ddot{a}_x = A_x \cdot \text{SA}$$

es decir, el valor presente actuarial de las primas iguala el valor presente actuarial del beneficio. $A_x$ es el precio de un seguro de vida entera (valor presente de 1 pagadero al momento de muerte), $\ddot{a}_x$ es la anualidad prepagable vitalicia. Es preciso usar $\Pi_x$ cuando el contexto es **una sola vida, modelo individual, con tablas de mortalidad y descuento financiero explícito**. En tu proyecto de cohortes con datos CNSF, la notación $\Pi_x$ es orientadora pero no directamente aplicable — trabajas con frecuencias observadas, no con tablas de mortalidad por construcción.

### 2.2 Prima de riesgo o prima pura de tarifa

En pricing moderno (y en tu proyecto), es el resultado del modelo:

$$\hat{\Pi} = \hat{F} \times \hat{S}_{\text{media}}$$

es decir, la frecuencia estimada por la severidad media estimada. Es lo que GLM y XGBoost compiten por estimar mejor.

### 2.3 Prima comercial o de tarifa

Lo que el asegurado paga. Se construye sobre la prima neta agregando tres capas:

$$\Pi^{\text{comercial}} = \frac{\Pi^{\text{neta}} + \text{Gastos de administración} + \text{Gastos de adquisición}}{1 - \text{Margen de utilidad}}$$

| Componente | Qué representa |
|---|---|
| Prima neta | Costo esperado del siniestro |
| Gastos de administración | Operación interna (salarios, sistemas, reservas) |
| Gastos de adquisición | Comisiones a agentes y canales |
| Margen de utilidad | Retorno sobre capital ajustado por riesgo |

**El techo de la prima** no es matemático sino de mercado y regulación: la CNSF no impone un límite explícito en vida individual, pero el mercado (competencia entre aseguradoras) y la capacidad de pago del asegurado actúan como límite natural. Lo que sí existe regulatoriamente es la obligación de demostrar que la prima es *suficiente* (no que es *máxima*).

---

## 3. El modelo colectivo de riesgo y su aplicación en vida individual

El modelo estándar es:

$$S = \sum_{i=1}^{N} Y_i$$

Cada término tiene su significado preciso:

| Símbolo | Nombre técnico | En Vida Individual |
|---|---|---|
| $S$ | Pérdida agregada (*aggregate loss*) | Siniestralidad total del portafolio o cohorte |
| $N$ | Frecuencia de siniestros | Número de muertes en el período |
| $Y_i$ | Severidad del $i$-ésimo siniestro | Monto pagado en la $i$-ésima reclamación |

### ¿$Y_i$ es la suma asegurada?

**En vida individual: sí, con matices.**

En un seguro de vida puro (*term life* o vida entera sin riders), el siniestro tiene un único resultado posible: la muerte activa el pago de la suma asegurada (SA) pactada. Por tanto:

- $Y_i = \text{SA}_i$ (la suma asegurada de la póliza $i$ que falleció)
- Si todas las pólizas tienen la misma SA, la severidad es **constante** (degenerada), no una variable aleatoria con dispersión real.
- Si las SA varían entre pólizas (que es lo habitual), la "distribución de severidad" es en realidad la **distribución de sumas aseguradas en el portafolio**, no una distribución de pérdidas aleatorias como en daños.

Esto es una diferencia fundamental con automóviles o salud, donde el monto del siniestro es incierto incluso después de que ocurre el evento.

### Una sola reclamación posible: ¿por qué hablan de severidades "continuas" en vida?

Tienes razón: en un seguro de vida individual, **solo puede haber un siniestro por póliza** (nadie muere dos veces). La continuidad no se refiere al número de reclamaciones sino al **tiempo de muerte** $T_x$, que sí es una variable aleatoria continua:

$$T_x \sim \text{distribución de tiempo de vida residual de } (x)$$

El seguro de vida de largo plazo (toda la vida, o dotal) descuenta ese pago: importa *cuándo* muere el asegurado, no solo *si* muere. De ahí que el precio involucre tablas de mortalidad y tasas de descuento.

En tu proyecto con datos anuales de CNSF, el tiempo continuo colapsa a un indicador binario: **¿murió en el año de observación?** La frecuencia se convierte en:

$$N \sim \text{Binomial}(n_{\text{expuestos}},\, q_x)$$

o, cuando $n$ es grande y $q_x$ es pequeño, aproximada por Poisson.

---

## 4. Cotas de la prima: piso y techo

### Piso: principio de equivalencia actuarial

$$\Pi^{\text{neta}} \geq \mathbb{E}[S]$$

En la práctica, la igualdad define la prima mínima técnicamente sostenible. Cobrar menos implica subsidio cruzado (que puede ser intencional) o pérdida esperada.

### Techo: no es matemático

| Restricción | Naturaleza | Fuente |
|---|---|---|
| Suficiencia | La prima debe cubrir $\mathbb{E}[S]$ + gastos + reservas | Regulación CNSF (Circular Única) |
| Equidad | No discriminación arbitraria por variables no técnicas | Principios actuariales y regulación |
| Competencia | La prima no puede ser tan alta que pierda mercado | Mercado |
| Asequibilidad | Implícita: el asegurado debe poder pagar | Mercado y diseño de producto |

La CNSF no fija un precio máximo en vida individual, pero el **registro de notas técnicas** exige que la prima sea justificable actuarialmente. Un modelo ML que produce una prima que no puede explicarse en términos causales tiene fricción regulatoria — ese es el trade-off central de tu investigación.

---

## 5. Cómo se comparan modelos: ¿GLM suma o resta vs ML?

Un modelo "es mejor" solo en relación a una métrica definida sobre datos que no vio en entrenamiento.

### Las dos dimensiones que importan en pricing

**Discriminación** — ¿El modelo ordena bien los riesgos?

$$\text{Gini} = 2 \cdot \text{AUC} - 1$$

Un Gini alto significa que el modelo separa bien las cohortes de alta siniestralidad de las de baja siniestralidad. GLM y ML pueden compararse aquí directamente.

**Calibración** — ¿La prima estimada es insesgada en promedio?

$$\text{Ratio de calibración} = \frac{\sum \hat{\Pi}_i}{\sum S_i^{\text{observado}}} \approx 1$$

Un modelo puede discriminar muy bien (Gini alto) pero estar sistemáticamente sesgado — por ejemplo, subestimar siempre la siniestralidad en cohortes de edad avanzada. En ese caso, no es usable en pricing sin recalibración.

### Métricas por target en tu proyecto

| Target | Métrica recomendada | Por qué |
|---|---|---|
| Frecuencia de siniestros | Deviance de Poisson | Es la pérdida canónica para conteos |
| Severidad media | Deviance de Gamma | Penaliza errores multiplicativos |
| Prima pura (frecuencia × severidad) | Deviance de Tweedie | Combina ambas distribuciones |
| Ranking de riesgo | Coeficiente de Gini | Comparación directa GLM vs ML |

### El veredicto que buscas

```
Si Gini(ML) - Gini(GLM) >> 0  →  ML discrimina mejor
Si |Calibración(ML) - 1| < |Calibración(GLM) - 1|  →  ML también está mejor calibrado
Si ambas condiciones se cumplen  →  ML domina a GLM en desempeño puro

Pero: ¿puede el regulador auditar la tarifa de ML?
      ¿puede el actuario responsable firmarla?
      Ese es el costo de interpretabilidad.
```

---

## 6. Glosario de términos clave para el proyecto

| Término | Definición precisa | Nota para el proyecto |
|---|---|---|
| **Exposición** | Tiempo-persona bajo riesgo en el período (en años o fracción) | En datos CNSF anuales, se aproxima como número de pólizas en vigor |
| **Frecuencia** | Siniestros / Exposición | Target principal de tu modelo de frecuencia |
| **Severidad** | Monto pagado por siniestro | En vida individual ≈ suma asegurada media de quienes fallecen |
| **Siniestralidad** | Prima neta consumida = Frecuencia × Severidad | Es lo que el modelo de Tweedie estima directamente |
| **Prima devengada** | Porción de la prima correspondiente al período transcurrido | Base del denominador del loss ratio |
| **Cohorte** | Grupo de pólizas homogéneo por variables de segmentación | En tu proyecto: `ANIO × ENTIDAD × SEXO × EDAD × COBERTURA × PLAN` |
| **Nota técnica** | Documento actuarial que justifica la tarifa ante la CNSF | Lo que ML amenaza: un XGBoost no produce una nota técnica auditable trivialmente |
| **Estudio de experiencia** | Contraste mortalidad/siniestralidad observada vs esperada | Es exactamente lo que puedes hacer con tus datos 2021–2024 |
| **$q_x$** | Probabilidad de muerte en el año para una vida de edad $x$ | Sale de tablas de mortalidad; en tu proyecto la estimas empíricamente por cohorte |
| **$A_x$** | Valor presente actuarial de 1 pagadero al momento de muerte de $(x)$ | Requiere tabla de mortalidad + tasa de descuento; no observable directamente en tus datos |
| **$\ddot{a}_x$** | Anualidad prepagable vitalicia sobre $(x)$ | Relaciona primas periódicas con prima única |
| **Loss ratio** | Siniestros / Prima devengada | Métrica de negocio; tu validación externa más importante |
| **IBNR** | Siniestros incurridos pero no reportados | Relevante en daños más que en vida, pero existe en vida colectivo |

---

---

# ANEXO: Otros seguros — contrastes de referencia

> Este anexo es solo para sensibilizar que las distribuciones, el número de siniestros posibles y los conceptos cambian de ramo a ramo. No es el foco del proyecto.

---

## A.1 Vida Grupo

### ¿Qué cambia respecto a Vida Individual?

| Dimensión | Vida Individual | Vida Grupo |
|---|---|---|
| **Unidad asegurada** | Una persona, una póliza | Un colectivo (empresa, sindicato) bajo una sola póliza maestra |
| **Suscripción** | Cada vida evaluada individualmente (cuestionario médico) | El grupo se suscribe en bloque; sin examen médico para cada integrante |
| **Anticorrelación** | Alta: los eventos de muerte son independientes | Puede haber correlación si el grupo comparte riesgos laborales |
| **Suma asegurada** | Fija en contrato individual | Puede ser múltiplo del salario o fija por convenio |
| **Renovación** | Vitalicia o a largo plazo | Anual; el grupo puede cambiar de tamaño |
| **Distribución de $N$** | Binomial($n$, $q_x$) por cohorte | Binomial($n_{\text{grupo}}$, $\bar{q}$) donde $\bar{q}$ es la tasa media del colectivo |

**Punto clave**: en vida grupo el actuario trabaja con la **ley de los grandes números dentro del grupo**. Si el grupo es grande, la siniestralidad observada converge rápido al valor esperado — lo que reduce el riesgo de fluctuación aleatoria. En grupos pequeños (< 50 vidas), el seguro se comporta casi como individual.

La siniestralidad esperada se estima como:

$$\mathbb{E}[S_{\text{grupo}}] = n \cdot \bar{q} \cdot \overline{\text{SA}}$$

La distribución de $S$ en grupos grandes tiende a Normal por TCL, lo que simplifica la reserva de fluctuación.

### Modelos relevantes

Para vida grupo, GLM sigue siendo el estándar, pero los features son características del grupo (giro industrial, distribución etaria, antigüedad promedio), no del individuo. ML puede capturar interacciones entre giro y distribución etaria que GLM linealiza.

---

## A.2 Daños — Automóviles

### Por qué daños es fundamentalmente distinto

En automóviles, **el siniestro no es binario ni de monto fijo**. Hay tres fenómenos simultáneos que no existen en vida individual:

1. **Frecuencia no trivial**: una unidad puede siniestrar 0, 1, 2 o más veces en un año. $N$ es genuinamente Poisson (o Negativa Binomial si hay sobredispersión).
2. **Severidad incierta y continua**: el monto del daño ($Y_i$) es desconocido hasta la liquidación del siniestro. Se distribuye típicamente como Gamma o Log-Normal.
3. **IBNR real**: los siniestros de daños a terceros pueden reportarse meses después del evento. En vida individual, la muerte se reporta rápido.

### Estructura del modelo colectivo en autos

$$S = \sum_{i=1}^{N} Y_i \quad \text{con } N \sim \text{Poisson}(\lambda) \text{ y } Y_i \sim \text{Gamma}(\alpha, \beta)$$

| Componente | Vida Individual | Automóviles |
|---|---|---|
| $N$ | Bernoulli($q_x$): 0 o 1 | Poisson($\lambda$): 0, 1, 2, ... |
| $Y_i$ | SA pactada (constante o casi constante) | Variable aleatoria continua: desde 0 hasta límite de cobertura |
| Correlación $N$–$Y_i$ | No aplica (si $N=0$, $S=0$ trivialmente) | Puede existir: conductores que chocan más también dañan más |
| Distribución de $S$ | Mezcla discreta dominada por el punto de masa en 0 | Distribución Tweedie (mezcla Poisson-Gamma) |

### Features relevantes en dautos vs vida

| Feature | Vida Individual | Automóviles |
|---|---|---|
| Edad | Mortalidad creciente en edades altas | Riesgo en jóvenes (16–25) y adultos mayores |
| Sexo | Diferencial actuarial relevante (validado en tablas) | Menor diferencial; regulación creciente lo restringe |
| Zona geográfica | Relevante (ENTIDAD en CNSF) | Muy relevante: delincuencia, densidad vial, clima |
| Características del bien | No aplica | Modelo, año, valor del vehículo — son los mejores predictores |
| Comportamiento | No observable ex ante | Telemetría (telematics): abre la puerta a pricing basado en conducción |

### Por qué ML domina antes en autos que en vida

En automóviles, la complejidad de las interacciones entre features (zona × tipo de vehículo × perfil del conductor) es alta y no lineal — territorio natural de árboles de decisión. En vida individual, los únicos features regulatorios permitidos (edad, sexo, cobertura) son pocos y sus efectos son monótonos, lo que da poco espacio para que ML supere al GLM con interacciones simples.

**Esta asimetría es relevante para tu investigación**: si ML gana en tu proyecto con datos CNSF de vida individual, el hallazgo es más sorprendente — y más publicable — que si lo hiciera en automóviles.

---

## Referencias

1. **Klugman, S.A., Panjer, H.H., Willmot, G.E.** (2019). *Loss Models: From Data to Decisions* (5a ed.). Wiley. — Referencia canónica para modelos de riesgo colectivo, distribuciones de severidad y frecuencia.

2. **Bowers, N.L. et al.** (1997). *Actuarial Mathematics* (2a ed.). Society of Actuaries. — Base de la notación $\Pi_x$, $A_x$, $\ddot{a}_x$ y el modelo individual de vida.

3. **de Jong, P. & Heller, G.Z.** (2008). *Generalized Linear Models for Insurance Data*. Cambridge University Press. — GLM aplicado a pricing; el puente entre la actuaría tradicional y el ML.

4. **Noll, A., Salzmann, R. & Wüthrich, M.V.** (2020). *Case Study: French Motor Third-Party Liability Claims*. SSRN 3164764. — Benchmark empírico de GLM vs ML en seguros; metodología directamente extrapolable a tu proyecto.

5. **CNSF — Circular Única de Seguros y Fianzas** (vigente). Capítulo 6: Operaciones y Ramos. — Marco regulatorio mexicano para notas técnicas y suficiencia de prima.
