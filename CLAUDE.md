## ML-for-Insurance

Claude originalmente la idea de mi proyecto era la siguiente:

mi_proyecto_ml/
├── venv/                           👈 entorno virtual (ignóralo en git)
├── docs/
    ├── Modelos_Reserva_CUSF.pdf    👈 datos de terceros
    └── Requerimiento_Capital_Solvencia_CUSF.pdf
├── data/
│   ├── raw/                         👈 datos originales
│   ├── processed/                  👈 datos limpios
│   └── external/                   👈 datos de terceros
├── notebooks/
│   ├── exploracion.ipynb
│   └── pruebas.ipynb
├── src/
│   ├── __init__.py
│   ├── features.py
│   ├── model.py
│   └── utils.py
├── tests/
│   └── test_model.py
├── requirements.txt
└── README.md
└── CLAUDE.md

Ahora que estoy más documentado tanto del proyecto como del la estructura, quiero algo más modular, y aqui empieza el contexto. No tengo experiencia en proyectos reales o en producción de Machine Learnig, empecemos por ahi, que si tengo:

- VSC (nivel básico, pero escalable facilmente)
- nvim (para no depender de un IDE y tener un editor profesional)
- OS Debian 12 bookworm
- Conozco las librerías estandar: numpy, pandas, scipy, scikit-learn
- venv, pip, jupiter

Que no tengo y me da la impresión de que ocupare:

.claude/rules/
├── code-style.md
├── testing.md
├── api-conventions.md
└── security.md

.claude/skills/
├── security-review/
│   ├── SKILL.md
│   └── DETAILED_GUIDE.md
└── deploy/
    ├── SKILL.md
    └── templates/
        └── release-notes.md

Las estructuras anteriores son para CLAUDE CODE, pero si de algo sirven en este proyecto, no se si hay que agregarlas.

### El proyecto

Mi proyecto "ML-for-Insurance" es mi servicio social en la facultad de ciencias, el cual tengo la libertad de desarrollar independientemente, la responsable o tutora es solo eso, un responsable y alguien que supervisa y redirige si es necesario, pero los tiempos, las metodologías y resultados son mios. Para que tengas la idea global te comparto el fichero "Modelos_Reserva_CUSF.pdf" y "Requerimiento_Capital_Solvencia_CUSF.pdf" que es un resumen del anterior.

Granulando el proyecto, que deberia hacer, ya que la conceptualización ya es compleja y los modelos aún más, que si tiene que hacer este proyecto:

- Partir de los modelos actuariales aceptados por la CUSF: Chain Lander, Boostrap, Simulación Estatutaria, etc. Es decir necesito generar resultados con estos modelos con los datos que extraiga "https://www.cnsf.gob.mx/EntidadesSupervisadas/InstitucionesSociedadesMutualistas/Paginas/DetalladaSeguros.aspx" ahi encuentro "Vida", "Accidente y Enfermedades", "Automoviles", solo voy escoger uno de los 3, aún no se cual, para todos hay datos.
- Como atacar el "99.5% Nivel de Confianza VaR a 1 año. Requisito matemático duro: cualquier método debe garantizar este umbral de solvencia".
- Que modelos de caja negra son viables para contrastar "Modelos Internos Vs Fórmula Estándar".
- Testeo Vs Legislación, parte técnica. Los modelos que proponga deben satisfacer: Estadísticos y Metodologías, Auditoría y Gobierno Corporativo, Prueba de Utilización.

Conclusión (temporal, esperando tu output):

- Crea la estructura ideal para mi contexto
- Crea el README.md con los requisitos para usar el repo: Objetivo, venv, pip install, requirements.txt, es decir, la carta de presentación del proyecto, y que debes hacer para clonarlo y usarlo
- Reescribir este fichero CLAUDE.md formalazando lo que un agente necesita para entender que estoy haciendo con solo compartir el fichero.

**Critico**: Proyecto diseñado para trabajarlo durante 6 meses, es decir, estima y construye un plan de trabajo para que tu CLAUDE.md distribuya el trabajo en 6 meses, alcanzando la meta o target de transparentar modelos de caja negra para el cálculo de reservas con ML.
