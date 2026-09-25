"""Tests de ejemplo para src/validador/lector.py."""

import pytest

from validador.lector import leer_csv


def test_req_2_1_csv_no_existe(tmp_path):
    """Archivo inexistente levanta OSError."""
    ruta = str(tmp_path / "no_existe.csv")
    with pytest.raises(OSError):
        leer_csv(ruta, ",")


def test_req_2_2_bom_eliminado(tmp_path):
    """CSV con BOM de Excel: el primer campo de la cabecera no comienza con \\ufeff."""
    ruta = tmp_path / "con_bom.csv"
    # Escribe bytes con BOM manualmente para garantizar su presencia
    ruta.write_bytes(b"\xef\xbb\xbfid_venta,cliente\n1,Ana\n")
    cabecera, filas = leer_csv(str(ruta), ",")
    assert not cabecera[0].startswith("\ufeff"), (
        f"El primer campo de la cabecera no debe contener BOM; se obtuvo: {cabecera[0]!r}"
    )
    assert cabecera[0] == "id_venta"


def test_req_2_3_numeracion_excel(tmp_path):
    """El primer dato tiene numero == 2 (convencion Excel: cabecera=1, primer dato=2)."""
    ruta = tmp_path / "datos.csv"
    ruta.write_text("col1,col2\nval1,val2\n", encoding="utf-8")
    cabecera, filas = leer_csv(str(ruta), ",")
    assert len(filas) == 1
    assert filas[0].numero == 2


def test_req_2_4_delimitador_personalizado(tmp_path):
    """CSV con delimitador '|' se lee correctamente."""
    ruta = tmp_path / "pipe.csv"
    ruta.write_text("id_venta|cliente|valor\n1|Ana|100.0\n", encoding="utf-8")
    cabecera, filas = leer_csv(str(ruta), "|")
    assert cabecera == ["id_venta", "cliente", "valor"]
    assert len(filas) == 1
    assert filas[0].campos["id_venta"] == "1"
    assert filas[0].campos["cliente"] == "Ana"
    assert filas[0].campos["valor"] == "100.0"


def test_req_2_5_csv_sin_datos(tmp_path):
    """CSV con solo cabecera devuelve lista de filas vacia."""
    ruta = tmp_path / "solo_cabecera.csv"
    ruta.write_text("col1,col2\n", encoding="utf-8")
    cabecera, filas = leer_csv(str(ruta), ",")
    assert cabecera == ["col1", "col2"]
    assert filas == []


# ---------------------------------------------------------------------------
# Property tests — Hypothesis (tarea 3.3)
# ---------------------------------------------------------------------------

import io
import os
import tempfile

from hypothesis import given, settings
from hypothesis import strategies as st


# Estrategia: nombres de columna simples (solo letras ASCII para evitar
# problemas con caracteres especiales en CSV).
_nombre_col = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz_",
    min_size=1,
    max_size=10,
)

# Estrategia: valores de celda sin comas, saltos de línea ni comillas.
_valor_celda = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789 ",
    min_size=0,
    max_size=15,
)


def _escribir_csv_temp(contenido_bytes: bytes) -> str:
    """Escribe bytes en un archivo temporal y devuelve la ruta."""
    fd, ruta = tempfile.mkstemp(suffix=".csv")
    try:
        os.write(fd, contenido_bytes)
    finally:
        os.close(fd)
    return ruta


def _construir_csv_bytes(
    columnas: list[str],
    filas: list[list[str]],
    delimitador: str = ",",
    con_bom: bool = False,
) -> bytes:
    """Genera el contenido de un CSV como bytes."""
    buf = io.StringIO()
    buf.write(delimitador.join(columnas) + "\n")
    for fila in filas:
        buf.write(delimitador.join(fila) + "\n")
    texto = buf.getvalue()
    raw = texto.encode("utf-8")
    if con_bom:
        raw = b"\xef\xbb\xbf" + raw
    return raw


# ---------------------------------------------------------------------------
# Property 3: La numeracion de filas es consistente con Excel (Req 2.3)
# ---------------------------------------------------------------------------

# Feature: validador-csv, Propiedad 3: numeracion consistente con Excel
@given(n=st.integers(min_value=0, max_value=50))
@settings(max_examples=200)
def test_req_2_3_numeracion_propiedad(n: int) -> None:
    """Para cualquier CSV con N filas de datos, leer_csv devuelve una lista de
    longitud N donde fila[i].numero == i + 2 para todo i en [0, N).

    Validates: Requirements 2.3
    """
    columnas = ["col_a", "col_b"]
    filas_datos = [["valor1", "valor2"]] * n
    contenido = _construir_csv_bytes(columnas, filas_datos)
    ruta = _escribir_csv_temp(contenido)
    try:
        cabecera, filas = leer_csv(ruta, ",")
        assert len(filas) == n, f"Se esperaban {n} filas, se obtuvieron {len(filas)}"
        for i, fila in enumerate(filas):
            assert fila.numero == i + 2, (
                f"fila[{i}].numero deberia ser {i + 2}, pero es {fila.numero}"
            )
    finally:
        os.unlink(ruta)


# ---------------------------------------------------------------------------
# Property 4: El lector elimina el BOM de Excel (Req 2.2)
# ---------------------------------------------------------------------------

# Feature: validador-csv, Propiedad 4: BOM eliminado
@given(
    columnas=st.lists(
        _nombre_col.filter(lambda s: s.strip() != ""),
        min_size=1,
        max_size=5,
        unique=True,
    )
)
@settings(max_examples=200)
def test_req_2_2_bom_propiedad(columnas: list[str]) -> None:
    """Para cualquier CSV cuyo contenido sea identico salvo por la presencia o
    ausencia del BOM, la cabecera devuelta es la misma: el nombre de la primera
    columna no comienza con \\ufeff.

    Validates: Requirements 2.2
    """
    contenido_sin_bom = _construir_csv_bytes(columnas, [], con_bom=False)
    contenido_con_bom = _construir_csv_bytes(columnas, [], con_bom=True)

    ruta_sin = _escribir_csv_temp(contenido_sin_bom)
    ruta_con = _escribir_csv_temp(contenido_con_bom)
    try:
        cabecera_sin, _ = leer_csv(ruta_sin, ",")
        cabecera_con, _ = leer_csv(ruta_con, ",")

        assert cabecera_sin == cabecera_con, (
            f"Cabecera sin BOM {cabecera_sin!r} difiere de cabecera con BOM {cabecera_con!r}"
        )
        assert not cabecera_con[0].startswith("\ufeff"), (
            f"El primer campo de la cabecera no debe contener BOM: {cabecera_con[0]!r}"
        )
    finally:
        os.unlink(ruta_sin)
        os.unlink(ruta_con)
