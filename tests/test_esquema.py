"""Pruebas para src/validador/esquema.py.

Cubre los requisitos 1.1 – 1.6 con pruebas de ejemplo (tarea 2.4) y
pruebas de propiedades con Hypothesis (tarea 2.5).
"""

import json
import tempfile
import os

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from validador.esquema import (
    cargar_esquema,
    TIPOS_VALIDOS,
    FORMATO_FECHA_DEFAULT,
    DELIMITADOR_DEFAULT,
)


# ---------------------------------------------------------------------------
# Helpers de fixture
# ---------------------------------------------------------------------------

def _escribir_esquema_tmp(contenido: dict | str) -> str:
    """Escribe el contenido como JSON en un archivo temporal y devuelve la ruta."""
    fd, ruta = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if isinstance(contenido, str):
                f.write(contenido)
            else:
                json.dump(contenido, f, ensure_ascii=False)
    except Exception:
        os.unlink(ruta)
        raise
    return ruta


def _esquema_minimo(*, delimitador: str | None = None, columnas: list | None = None) -> dict:
    """Devuelve un dict de esquema válido mínimo."""
    datos: dict = {
        "columnas": columnas if columnas is not None else [
            {"nombre": "id", "tipo": "entero", "obligatoria": True}
        ]
    }
    if delimitador is not None:
        datos["delimitador"] = delimitador
    return datos


# ---------------------------------------------------------------------------
# Pruebas de ejemplo — tarea 2.4
# ---------------------------------------------------------------------------

def test_req_1_1_esquema_no_existe():
    """Archivo de esquema inexistente levanta OSError."""
    with pytest.raises(OSError):
        cargar_esquema("/ruta/que/no/existe/esquema.json")


def test_req_1_2_esquema_json_malformado(tmp_path):
    """JSON mal formado en el esquema levanta ValueError."""
    ruta = tmp_path / "malo.json"
    ruta.write_text("{esto no es json válido", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON"):
        cargar_esquema(str(ruta))


def test_req_1_3_delimitador_presente(tmp_path):
    """El delimitador definido en el esquema se respeta."""
    datos = _esquema_minimo(delimitador=";")
    ruta = tmp_path / "esquema.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    esquema = cargar_esquema(str(ruta))
    assert esquema.delimitador == ";"


def test_req_1_3_delimitador_ausente(tmp_path):
    """Sin campo delimitador se usa la coma como valor por defecto."""
    datos = _esquema_minimo()
    ruta = tmp_path / "esquema.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    esquema = cargar_esquema(str(ruta))
    assert esquema.delimitador == DELIMITADOR_DEFAULT


def test_req_1_4_tipo_desconocido(tmp_path):
    """Un tipo de columna desconocido levanta ValueError."""
    datos = _esquema_minimo(columnas=[
        {"nombre": "activo", "tipo": "booleano", "obligatoria": True}
    ])
    ruta = tmp_path / "esquema.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    with pytest.raises(ValueError, match="Tipo desconocido"):
        cargar_esquema(str(ruta))


def test_req_1_5_formato_fecha_presente(tmp_path):
    """El formato de fecha personalizado se almacena en la columna."""
    datos = _esquema_minimo(columnas=[
        {"nombre": "fecha", "tipo": "fecha", "obligatoria": True, "formato": "%d/%m/%Y"}
    ])
    ruta = tmp_path / "esquema.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    esquema = cargar_esquema(str(ruta))
    col_fecha = esquema.columnas[0]
    assert col_fecha.formato == "%d/%m/%Y"


def test_req_1_5_formato_fecha_ausente(tmp_path):
    """Sin campo formato en columna de fecha se usa el default '%Y-%m-%d'."""
    datos = _esquema_minimo(columnas=[
        {"nombre": "fecha", "tipo": "fecha", "obligatoria": True}
    ])
    ruta = tmp_path / "esquema.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    esquema = cargar_esquema(str(ruta))
    col_fecha = esquema.columnas[0]
    assert col_fecha.formato == FORMATO_FECHA_DEFAULT


def test_req_1_6_campo_columnas_ausente(tmp_path):
    """JSON sin el campo 'columnas' levanta ValueError."""
    datos = {"delimitador": ","}
    ruta = tmp_path / "esquema.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    with pytest.raises(ValueError, match="columnas"):
        cargar_esquema(str(ruta))


# ---------------------------------------------------------------------------
# Pruebas de propiedad con Hypothesis — tarea 2.5
# ---------------------------------------------------------------------------

# Property 1: El delimitador del esquema se respeta fielmente.
# Validates: Requirements 1.3
@given(
    delimitador=st.text(
        alphabet=st.characters(whitelist_categories=("L", "N", "P", "S")),
        min_size=1,
        max_size=1,
    )
)
@settings(max_examples=200)
def test_req_1_3_delimitador_propiedad(delimitador):
    """Para cualquier caracter d, cargar_esquema devuelve Esquema con delimitador == d.

    Feature: validador-csv, Propiedad 1: el delimitador del esquema se respeta fielmente.
    Validates: Requirements 1.3
    """
    # Caracteres problemáticos para JSON como valores de cadena son pocos;
    # excluimos solo los que romperían la serialización JSON del propio delimitador.
    assume("\x00" not in delimitador)

    datos = _esquema_minimo(delimitador=delimitador)
    ruta = None
    try:
        ruta = _escribir_esquema_tmp(datos)
        esquema = cargar_esquema(ruta)
        assert esquema.delimitador == delimitador
    finally:
        if ruta and os.path.exists(ruta):
            os.unlink(ruta)


# Property 2: Tipos desconocidos en el esquema son rechazados.
# Validates: Requirements 1.4
@given(
    tipo=st.text(min_size=1, max_size=30).filter(lambda t: t not in TIPOS_VALIDOS)
)
@settings(max_examples=200)
def test_req_1_4_tipos_desconocidos_propiedad(tipo):
    """Para cualquier cadena fuera de TIPOS_VALIDOS, cargar_esquema levanta ValueError.

    Feature: validador-csv, Propiedad 2: tipos desconocidos en el esquema son rechazados.
    Validates: Requirements 1.4
    """
    # Nos aseguramos de que la cadena no sea uno de los tipos válidos.
    assume(tipo not in TIPOS_VALIDOS)

    datos = _esquema_minimo(columnas=[
        {"nombre": "col1", "tipo": tipo, "obligatoria": True}
    ])
    ruta = None
    try:
        ruta = _escribir_esquema_tmp(datos)
        with pytest.raises(ValueError):
            cargar_esquema(ruta)
    finally:
        if ruta and os.path.exists(ruta):
            os.unlink(ruta)
