"""
Tests de smoke — verifican que el stack técnico completo esté disponible.
Ejecutar después de: pip install -r requirements.txt
"""


def test_core_stack():
    import numpy  # noqa: F401
    import pandas  # noqa: F401
    import scipy  # noqa: F401


def test_actuarial_stack():
    import chainladder  # noqa: F401


def test_ml_stack():
    import sklearn  # noqa: F401
    import pygam  # noqa: F401


def test_explainability_stack():
    import shap  # noqa: F401


def test_stats_stack():
    import statsmodels  # noqa: F401
