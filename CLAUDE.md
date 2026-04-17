# CLAUDE.md — Contexto del proyecto para agentes de IA

> **Instrucción para el agente**: Este fichero es la fuente de verdad del proyecto. Léelo completo antes de responder cualquier pregunta o ejecutar cualquier tarea. Contiene el objetivo, el marco regulatorio, la arquitectura técnica, las convenciones del código y el plan de trabajo de 6 meses. No asumas nada que no esté aquí documentado.

---

## 1. Identidad del proyecto

| Campo | Valor |
|---|---|
| Nombre | ML-for-Insurance |
| Tipo | Paper académico |
| Institución | Facultad de Ciencias, UNAM |
| Autor | Gabriel Fernando Rosas Zepeda |
| Duración | 6 meses (inicio: mayo 2026) |
| Autonomía | Alta — el autor define metodologías y resultados; la tutora supervisa y redirige si es necesario |

---

## 2. Objetivo central

Investigar si modelos de **Machine Learning interpretable** pueden contrastar con los métodos actuariales estándar reconocidos por la CNSF para el cálculo de Reservas Técnicas y el Requerimiento de Capital de Solvencia (RCS), y en qué condiciones una **arquitectura híbrida** (actuarial + ML) satisface los requisitos normativos de la CUSF para ser aprobada como Modelo Interno.

**Hipótesis de trabajo**: Los modelos de ML de caja negra pura son inviables bajo CUSF. La única ruta viable es una arquitectura híbrida donde el componente ML actúa como estimador de frecuencias/severidades dentro de un armazón actuarial explícito y auditable.

---

## 3. Marco regulatorio (no negociable)

El proyecto está completamente contenido dentro de la **Circular Única de Seguros y Fianzas (CUSF)** de la CNSF, versión compulsada al 07-10-2024.

### 3.1 Ecuación central de reservas

```
Reserva Técnica = BEL (Mejor Estimación) + MR (Margen de Riesgo)
```

- **BEL**: media ponderada por probabilidad de flujos futuros, descontada con curvas libres de riesgo CNSF.
- **MR**: RCS futuros × tasa de costo de capital (~10 %) traídos a valor presente.

### 3.2 Métodos actuariales reconocidos por la CUSF (Parte I del proyecto)

| Método | Rol | Módulo en src/ |
|---|---|---|
| Chain Ladder | Base obligatoria para IBNR. Proyecta siniestros con link-ratios históricos | `src/actuarial/chain_ladder.py` |
| Bornhuetter-Ferguson | IBNR para carteras jóvenes. Combina experiencia observada con estimación a priori | `src/actuarial/bornhuetter_ferguson.py` |
| Cape Cod | Variante de BF; calibra pérdida última desde prima devengada | `src/actuarial/cape_cod.py` |
| Mack | Extensión estocástica de CL. Calcula varianza e IC del BEL sin distribución paramétrica | `src/actuarial/mack.py` |
| Bootstrap | Remuestreo sobre residuos del triángulo. Genera distribuciones empíricas del IBNR | `src/actuarial/bootstrap.py` |
| Simulación Estatutaria | Asignada por la CNSF; no elegible por la institución. Se implementa como referencia | Dentro de `chain_ladder.py` |

### 3.3 Requerimiento de Capital de Solvencia (RCS)

- **Umbral duro**: VaR al **99.5 %** a horizonte de **1 año** — cualquier método debe garantizarlo.
- **Módulos del RCS**: Técnico + Financiero + Mercado + Capital Operacional, agregados con matrices de correlación CUSF fijas.
- **Fórmula Estándar**: usar los parámetros publicados por la CNSF → aprobación regulatoria expedita.
- **Modelo Interno**: sustituye total o parcialmente la fórmula estándar → exige cumplir los 13 requisitos del Cap. 6.9.

### 3.4 Los 13 obstáculos para modelos ML de caja negra (CUSF Cap. 6.9)

El proyecto debe demostrar explícitamente cómo la arquitectura propuesta responde a cada uno:

**Estadísticos y metodológicos (6):**
1. Distribución de probabilidad explícita al 99.5 %
2. Reproducibilidad por profesional independiente
3. Hipótesis, parámetros y fundamentos matemáticos declarados
4. Back-testing y atribución de pérdidas y ganancias (P&L Attribution)
5. Coherencia con métodos actuariales estándar (IAA / IASB / CNSF)
6. Demostración de equivalencia al 99.5 %

**Auditoría y gobierno corporativo (7):**
7. Comprensión por el Consejo de Administración
8. Explicación por los responsables del modelo
9. Transparencia en atribución de P&L por segmento
10. Auditoría interna efectiva
11. Revisión independiente y externa anual
12. Opinión favorable del experto independiente
13. Control de versiones y documentación de algoritmos (incluye entrega de código fuente a la CNSF)

**Prueba de utilización (2):**  
14. Uso efectivo en toma de decisiones durante ≥ 1 año  
15. Pruebas de estrés interpretables por el Consejo *(nota: la CUSF lista 13 requisitos totales; los de prueba de utilización son subsección de ese grupo)*

---

## 4. Fuente de datos

- **Portal**: [CNSF — Detallada de Seguros](https://www.cnsf.gob.mx/EntidadesSupervisadas/InstitucionesSociedadesMutualistas/Paginas/DetalladaSeguros.aspx)
- **Ramos disponibles**: Vida · Accidentes y Enfermedades · Automóviles
- **Ramo seleccionado**: Por definir en el Sprint 1 según calidad y volumen de los datos disponibles
- **Criterio de selección**: el ramo con triángulos de desarrollo más largos y completos (mínimo 5 años de origen)
- Los datos descargados van a `data/raw/` y **nunca se versionan**

---

## 5. Stack técnico

### 5.1 Entorno del autor

| Herramienta | Nivel |
|---|---|
| Debian 12 Bookworm | OS de trabajo |
| Python 3.11 | Lenguaje principal |
| venv + pip | Gestión de entorno y dependencias |
| Jupyter Notebook | Exploración y prototipado |
| VSCode | IDE principal |
| Neovim | Editor secundario (sin dependencia de IDE) |
| Git + GitHub | Control de versiones |

### 5.2 Librerías principales

| Librería | Propósito |
|---|---|
| `chainladder` | Todos los métodos actuariales estándar CUSF |
| `pygam` | Generalized Additive Models (ML interpretable) |
| `scikit-learn` | Árboles de profundidad limitada, pipelines, validación cruzada |
| `shap` | Explicabilidad global a nivel portafolio |
| `scipy` / `statsmodels` | Distribuciones de pérdidas, back-testing, tests estadísticos |
| `arch` | VaR, modelos de volatilidad |
| `numpy` / `pandas` | Manipulación de datos y triángulos |
| `matplotlib` / `plotly` | Visualización y reportes |

### 5.3 Lo que no se usa (y por qué)

- **Redes neuronales profundas** (TensorFlow, PyTorch): inviables bajo CUSF por opacidad estructural
- **Gradient Boosting sin restricciones** (XGBoost, LightGBM): misma razón; pueden usarse con profundidad muy limitada como componente de estimación
- **AutoML**: incompatible con el requisito de hipótesis y parámetros explícitos

---

## 6. Arquitectura técnica objetivo

```
Datos CNSF
    │
    ▼
src/data_io/loader.py          ← Descarga y lectura de portal CNSF
src/data_io/preprocessor.py    ← Construcción de triángulos de desarrollo
    │
    ├──► src/actuarial/         ← Capa 1: Modelos actuariales estándar (Baseline)
    │        chain_ladder.py      → IBNR determinístico
    │        mack.py              → IC y varianza del BEL
    │        bootstrap.py         → Distribución empírica del IBNR
    │        bornhuetter_ferguson.py
    │        cape_cod.py
    │
    ├──► src/rcs/               ← Capa 2: RCS y VaR 99.5 %
    │        formula_estandar.py  → Módulos + matrices correlación CUSF
    │        var_calculator.py    → VaR sobre distribución de pérdidas
    │
    ├──► src/ml/                ← Capa 3: Componentes ML interpretables
    │        interpretable.py     → GAMs, árboles ≤ depth 4
    │        hibrido.py           → ML estima frecuencia/severidad → CL calcula IBNR
    │
    └──► src/explainability/    ← Capa 4: Explicabilidad regulatoria
             shap_global.py       → SHAP a nivel portafolio, atribución de riesgos por segmento
```

**Principio de diseño**: El modelo actuarial siempre es el motor de decisión del RCS. El componente ML es un insumo del motor, no el motor mismo.

---

## 7. Convenciones de código

- **Estilo**: PEP 8 · formateador `black` · linter `flake8`
- **Docstrings**: NumPy style — todas las funciones públicas documentadas con parámetros, returns y ejemplos
- **Tests**: `pytest` · cobertura mínima objetivo del 70 % en `src/`
- **Notebooks**: numerados con prefijo `NN_nombre_descriptivo.ipynb` · una sola responsabilidad por notebook
- **Commits**: mensajes en español, imperativo, máx. 72 caracteres. Ej: `Agrega implementación Chain Ladder con wrappers chainladder`
- **Ramas**: `main` (estable) · `sprint-N` (trabajo activo) · `feature/nombre-corto`
- **No se versionan**: datos, modelos entrenados (`.pkl`, `.joblib`), figuras generadas

---

## 8. Plan de trabajo — 6 meses

### Sprint 1 — Fundamentos y Datos (Mes 1)

**Objetivo**: Tener el entorno listo, los datos descargados y los primeros triángulos construidos.

**Semana 1-2:**
- Configurar repositorio GitHub con esta estructura
- Instalar y verificar todas las dependencias de `requirements.txt`
- Explorar el portal CNSF: entender la estructura de los archivos disponibles para Vida, A&E y Automóviles
- Implementar `src/data_io/loader.py`: descarga automática o semi-automática de datos

**Semana 3-4:**
- Implementar `src/data_io/preprocessor.py`: construir triángulos de desarrollo (pagos acumulados por año de origen × año de desarrollo)
- `notebooks/01_exploracion/`: EDA completo — calidad de datos, años disponibles, densidad del triángulo, valores atípicos
- **Decisión de ramo**: seleccionar Vida, A&E o Automóviles con justificación documentada en `docs/notas_tecnicas/sprint1_decision_ramo.md`

**Entregables del Sprint 1:**
- `data/raw/` poblado con datos CNSF
- `data/processed/triangulos_<ramo>.pkl`
- `notebooks/01_exploracion/EDA_triangulos.ipynb`
- `docs/notas_tecnicas/sprint1_decision_ramo.md`

---

### Sprint 2 — Modelos Actuariales Estándar (Mes 2)

**Objetivo**: Implementar y validar todos los métodos reconocidos por la CUSF. Este es el baseline obligatorio.

**Semana 1-2:**
- `src/actuarial/chain_ladder.py`: wrappers sobre `chainladder` library, cálculo de IBNR determinístico, factores de desarrollo, visualización de triángulos proyectados
- `src/actuarial/bornhuetter_ferguson.py`: estimación a priori de pérdida última, comparación con Chain Ladder
- `src/actuarial/cape_cod.py`: calibración desde prima devengada

**Semana 3-4:**
- `src/actuarial/mack.py`: varianza, intervalos de confianza del BEL, gráficas de IC
- `src/actuarial/bootstrap.py`: distribución empírica del IBNR (≥ 10,000 simulaciones), percentiles, histogramas
- `notebooks/02_actuarial/`: un notebook por método + un notebook de comparación consolidada
- Tabla comparativa: BEL, IC 95 %, estimación del IBNR para cada método

**Entregables del Sprint 2:**
- Los 5 módulos en `src/actuarial/` con tests en `tests/`
- `notebooks/02_actuarial/comparacion_metodos.ipynb`
- `docs/notas_tecnicas/sprint2_baseline_actuarial.md`

---

### Sprint 3 — RCS y VaR 99.5 % (Mes 3)

**Objetivo**: Implementar la Fórmula General del RCS y demostrar el umbral del 99.5 % con los modelos estándar.

**Semana 1-2:**
- `src/rcs/formula_estandar.py`: módulos de riesgo (técnico, financiero, mercado), matrices de correlación CUSF, cálculo del RCS agregado
- `src/rcs/var_calculator.py`: extracción del percentil 99.5 % desde la distribución Bootstrap del Sprint 2; comparación con RCS de fórmula estándar

**Semana 3-4:**
- `notebooks/03_rcs_var/`: notebook de fórmula estándar + notebook de VaR desde Bootstrap
- Demostración numérica: el Bootstrap estándar reproduce (o acota) el VaR 99.5 % de la fórmula estándar
- Análisis de sensibilidad: ¿qué pasa con el RCS si se cambia el ramo, el período de calibración o los factores de desarrollo?
- Pruebas de estrés iniciales: escenarios con siniestralidad +20 %, +50 %, +100 %

**Entregables del Sprint 3:**
- `src/rcs/` completo con tests
- `notebooks/03_rcs_var/var_99_5_demostracion.ipynb`
- `docs/notas_tecnicas/sprint3_rcs_var.md`

---

### Sprint 4 — ML Interpretable como Contraste (Mes 4)

**Objetivo**: Entrenar modelos ML interpretables y contrastar su estimación de IBNR/BEL con los métodos actuariales.

**Semana 1-2:**
- `src/ml/interpretable.py`:
  - **GAMs** (`pygam`): modelar frecuencia y severidad de siniestros como funciones suaves de las variables de desarrollo
  - **Árboles de decisión** (`scikit-learn`, `max_depth ≤ 4`): interpretables estructuralmente, reglas explícitas
  - **Regresión logística regularizada** (Lasso/Ridge): para clasificación de siniestros IBNR/no-IBNR
- `notebooks/04_ml_interpretable/`: entrenamiento, validación cruzada, métricas (MAE, RMSE, R²)

**Semana 3-4:**
- Comparación directa: estimaciones del BEL por método actuarial vs. estimaciones ML
- Análisis de residuos: ¿qué captura el ML que Chain Ladder no captura?
- Verificación regulatoria preliminar: ¿cumplen los modelos ML interpretables con los requisitos estadísticos del Cap. 6.9?
- `docs/notas_tecnicas/sprint4_ml_vs_actuarial.md`: tabla de cumplimiento requisito a requisito

**Entregables del Sprint 4:**
- `src/ml/interpretable.py` con tests
- `notebooks/04_ml_interpretable/GAM_vs_ChainLadder.ipynb`
- `notebooks/04_ml_interpretable/arbol_decisión_IBNR.ipynb`
- `docs/notas_tecnicas/sprint4_ml_vs_actuarial.md`

---

### Sprint 5 — Arquitectura Híbrida y Explicabilidad (Mes 5)

**Objetivo**: Construir la arquitectura híbrida definitiva y demostrar explicabilidad global con SHAP.

**Semana 1-2:**
- `src/ml/hibrido.py`: integrar el componente ML como estimador de frecuencias y severidades dentro del pipeline de Chain Ladder / Bootstrap
  - El ML predice los factores de desarrollo → Chain Ladder proyecta el triángulo → Bootstrap genera la distribución de pérdidas → VaR 99.5 % sobre esa distribución
- Esto mantiene el motor de decisión del RCS como actuarial (auditable) mientras el ML aporta precisión en la estimación

**Semana 3-4:**
- `src/explainability/shap_global.py`:
  - SHAP values a nivel portafolio completo (no solo local)
  - Atribución de riesgos por segmento de actividad (P&L Attribution CUSF)
  - Gráficas de dependencia SHAP: relación entre variables de desarrollo y contribución al BEL
- `notebooks/05_hibrido/`: comparación híbrido vs. puro actuarial vs. puro ML
- Tabla de cumplimiento actualizada: mapear los 13 requisitos CUSF contra la arquitectura híbrida

**Entregables del Sprint 5:**
- `src/ml/hibrido.py` y `src/explainability/shap_global.py` con tests
- `notebooks/05_hibrido/arquitectura_hibrida.ipynb`
- `notebooks/05_hibrido/shap_atribucion_portafolio.ipynb`
- `docs/notas_tecnicas/sprint5_arquitectura_hibrida.md`

---

### Sprint 6 — Validación, Back-testing y Memoria Técnica (Mes 6)

**Objetivo**: Validar el modelo completo contra legislación CUSF y producir la memoria técnica final.

**Semana 1-2:**
- `notebooks/06_validacion/`:
  - **Back-testing**: comparar predicciones del modelo híbrido contra siniestros reales de períodos anteriores
  - **Pruebas de robustez**: estabilidad del modelo ante variaciones en los datos de entrada
  - **Pruebas de estrés**: escenarios extremos (catástrofe, inflación de siniestros, crisis de liquidez) con interpretación causal
  - **P&L Attribution formal**: cada pérdida atribuida a factores de riesgo específicos, compatible con requisito CUSF 2.1.4

**Semana 3-4:**
- Auditoría de cumplimiento final: tabla completa de los 13 requisitos CUSF con evidencia de cumplimiento o justificación de mitigación para cada uno
- `docs/notas_tecnicas/memoria_tecnica_final.md`: documento de entrega académica
- Limpieza del repositorio: docstrings completos, README actualizado, tests con cobertura ≥ 70 %
- **Conclusiones**: ¿La arquitectura híbrida satisface los requisitos de la CUSF? ¿Qué requeriría para ser aprobada como Modelo Interno real?

**Entregables del Sprint 6:**
- `notebooks/06_validacion/` completo
- `docs/notas_tecnicas/memoria_tecnica_final.md`
- Repositorio GitHub limpio y documentado para entrega académica

---

## 9. Mapa del proyecto (resumen ejecutivo para el agente)

```
PREGUNTA CENTRAL
¿Puede ML transparentar y mejorar el cálculo de reservas técnicas bajo CUSF?

RESTRICCIÓN DURA
VaR 99.5 % a 1 año · 13 requisitos Cap. 6.9 CUSF · No caja negra pura

ESTRATEGIA
Baseline actuarial (CL + Mack + Bootstrap) → ML interpretable como contraste
→ Arquitectura híbrida (ML estima, actuarial decide) → SHAP global valida

ÉXITO DEL PROYECTO
El modelo híbrido reproduce el VaR 99.5 % del baseline actuarial
y satisface los requisitos estadísticos y de explicabilidad del Cap. 6.9
```

---

## 10. Preguntas frecuentes para el agente

**¿Cuál es el ramo de seguros seleccionado?**  
Por definir en Sprint 1. El agente debe revisar `docs/notas_tecnicas/sprint1_decision_ramo.md` si existe.

**¿Qué modelo ML es el central?**  
GAMs (`pygam`) como modelo principal de estimación, complementado con árboles de profundidad ≤ 4. No redes neuronales.

**¿Qué librería actuarial se usa?**  
`chainladder` (Python) — cubre Chain Ladder, BF, Cape Cod, Mack y Bootstrap. Ver `requirements.txt`.

**¿Qué pasa si un método de ML no cumple un requisito CUSF?**  
Se documenta el obstáculo en la nota técnica del sprint correspondiente y se propone la vía de mitigación del Cap. 2.5 del documento CUSF de referencia.

**¿Este proyecto busca aprobación regulatoria real?**  
No. Es un proyecto de investigación académica. El objetivo es demostrar qué condiciones serían necesarias para que una arquitectura híbrida fuera aprobable, no obtener la aprobación misma.
