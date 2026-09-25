"""Tests para src/validador/reglas.py.

Cubre el modelo de datos Hallazgo y las reglas de validacion.
"""

import dataclasses

import pytest

from validador.reglas import Hallazgo


# ---------------------------------------------------------------------------
# Tarea 1.3 — modelo de datos Hallazgo
# ---------------------------------------------------------------------------


def test_req_0_hallazgo_construccion_correcta() -> None:
    """Verifica que los cinco campos de Hallazgo se asignan correctamente."""
    hallazgo = Hallazgo(
        fila=2,
        columna="fecha",
        regla="tipo_invalido",
        valor="2026/09/02",
        mensaje="El valor '2026/09/02' no coincide con el formato %Y-%m-%d",
    )

    assert hallazgo.fila == 2
    assert hallazgo.columna == "fecha"
    assert hallazgo.regla == "tipo_invalido"
    assert hallazgo.valor == "2026/09/02"
    assert hallazgo.mensaje == "El valor '2026/09/02' no coincide con el formato %Y-%m-%d"


def test_req_0_hallazgo_es_inmutable() -> None:
    """Verifica que intentar modificar un campo de Hallazgo lanza FrozenInstanceError."""
    hallazgo = Hallazgo(
        fila=3,
        columna="cantidad",
        regla="tipo_invalido",
        valor="diez",
        mensaje="El valor 'diez' no es un entero valido",
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        hallazgo.fila = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Tarea 4.2 — tests de ejemplo para verificar_columnas_faltantes
# ---------------------------------------------------------------------------

from validador.esquema import ColumnaEsquema, Esquema
from validador.reglas import verificar_columnas_faltantes


def _esquema_simple(nombres: list[str], obligatorias: list[bool] | None = None) -> Esquema:
    """Construye un Esquema minimo a partir de nombres de columna."""
    if obligatorias is None:
        obligatorias = [True] * len(nombres)
    columnas = tuple(
        ColumnaEsquema(nombre=n, tipo="texto", obligatoria=o)
        for n, o in zip(nombres, obligatorias)
    )
    return Esquema(columnas=columnas, clave_unica=(), delimitador=",")


def test_req_3_1_columna_faltante_unica() -> None:
    """Una columna obligatoria ausente genera exactamente 1 hallazgo columna_faltante."""
    esquema = _esquema_simple(["id", "nombre", "fecha"])
    cabecera = ["id", "nombre"]  # falta "fecha"

    hallazgos = verificar_columnas_faltantes(cabecera, esquema)

    assert len(hallazgos) == 1
    assert hallazgos[0].regla == "columna_faltante"
    assert hallazgos[0].columna == "fecha"
    assert hallazgos[0].fila == 1
    assert hallazgos[0].valor == ""


def test_req_3_1_columnas_faltantes_multiples() -> None:
    """Dos columnas obligatorias ausentes generan exactamente 2 hallazgos."""
    esquema = _esquema_simple(["id", "nombre", "fecha", "monto"])
    cabecera = ["id"]  # faltan "nombre", "fecha", "monto"

    hallazgos = verificar_columnas_faltantes(cabecera, esquema)

    assert len(hallazgos) == 3
    assert all(h.regla == "columna_faltante" for h in hallazgos)
    assert all(h.fila == 1 for h in hallazgos)
    assert {h.columna for h in hallazgos} == {"nombre", "fecha", "monto"}


def test_req_3_3_todas_presentes() -> None:
    """Cuando todas las columnas obligatorias estan presentes, devuelve lista vacia."""
    esquema = _esquema_simple(["id", "nombre", "fecha"])
    cabecera = ["id", "nombre", "fecha"]

    hallazgos = verificar_columnas_faltantes(cabecera, esquema)

    assert hallazgos == []


def test_req_3_4_columna_extra_ignorada() -> None:
    """Columnas extra en la cabecera (no en el esquema) no generan hallazgo."""
    esquema = _esquema_simple(["id", "nombre"])
    cabecera = ["id", "nombre", "columna_extra"]

    hallazgos = verificar_columnas_faltantes(cabecera, esquema)

    assert hallazgos == []


def test_req_3_5_case_sensitive() -> None:
    """La comparacion es sensible a mayusculas: 'Fecha' != 'fecha'."""
    esquema = _esquema_simple(["fecha"])
    cabecera = ["Fecha"]  # diferente capitalización

    hallazgos = verificar_columnas_faltantes(cabecera, esquema)

    assert len(hallazgos) == 1
    assert hallazgos[0].columna == "fecha"


# ---------------------------------------------------------------------------
# Tarea 4.3 — property test para verificar_columnas_faltantes (Property 5)
# ---------------------------------------------------------------------------

from hypothesis import given, settings
from hypothesis import strategies as st

# Estrategia: nombres de columna formados solo por letras minusculas y guion bajo
_nombre_col = st.text(alphabet="abcdefghijklmnopqrstuvwxyz_", min_size=1, max_size=15)


# Feature: validador-csv, Propiedad 5: columnas faltantes detectadas todas y solo ellas
@given(
    todas=st.lists(_nombre_col, min_size=1, max_size=10, unique=True),
    num_ausentes=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=200)
def test_req_3_1_columnas_faltantes_propiedad(todas: list[str], num_ausentes: int) -> None:
    """Property 5: para cualquier subconjunto F de obligatorias ausentes,
    verificar_columnas_faltantes genera exactamente |F| hallazgos de tipo
    columna_faltante, todos con fila=1.

    Validates: Requirements 3.1
    """
    # Cuantas columnas realmente se pueden ausentar (no mas que el total disponible)
    ausentes_reales = min(num_ausentes, len(todas))
    ausentes: set[str] = set(todas[:ausentes_reales])
    presentes: list[str] = [c for c in todas if c not in ausentes]

    # Construir esquema con todas las columnas como obligatorias
    esquema = _esquema_simple(todas)

    # La cabecera solo contiene las columnas presentes
    hallazgos = verificar_columnas_faltantes(presentes, esquema)

    # Exactamente |F| hallazgos
    assert len(hallazgos) == len(ausentes), (
        f"Esperados {len(ausentes)} hallazgos, obtenidos {len(hallazgos)}. "
        f"Ausentes: {ausentes}, presentes en cabecera: {presentes}"
    )

    # Todos de tipo columna_faltante con fila=1
    for h in hallazgos:
        assert h.regla == "columna_faltante", f"Regla inesperada: {h.regla}"
        assert h.fila == 1, f"Fila inesperada: {h.fila}"
        assert h.valor == "", f"Valor inesperado: {h.valor!r}"

    # El conjunto de columnas en los hallazgos coincide exactamente con F
    columnas_hallazgos = {h.columna for h in hallazgos}
    assert columnas_hallazgos == ausentes, (
        f"Columnas en hallazgos {columnas_hallazgos} != ausentes esperadas {ausentes}"
    )


# ---------------------------------------------------------------------------
# Tarea 6.2 — tests de ejemplo para verificar_vacios (Regla 3)
# ---------------------------------------------------------------------------

from validador.lector import FilaCSV
from validador.reglas import verificar_tipos, verificar_vacios


def _esquema_vacios(nombres: list[str], obligatorias: list[bool]) -> Esquema:
    """Construye un Esquema con columnas de tipo texto según obligatoriedad indicada."""
    columnas = tuple(
        ColumnaEsquema(nombre=n, tipo="texto", obligatoria=o)
        for n, o in zip(nombres, obligatorias)
    )
    return Esquema(columnas=columnas, clave_unica=(), delimitador=",")


def test_req_5_1_vacio_en_obligatoria_genera_hallazgo() -> None:
    """Celda con cadena vacia en columna obligatoria genera exactamente 1 hallazgo vacio_obligatorio."""
    esquema = _esquema_vacios(["nombre"], [True])
    filas = [_fila(2, nombre="")]

    hallazgos = verificar_vacios(filas, esquema)

    assert len(hallazgos) == 1
    h = hallazgos[0]
    assert h.regla == "vacio_obligatorio"
    assert h.fila == 2
    assert h.columna == "nombre"


def test_req_5_1_espacios_en_obligatoria_genera_hallazgo() -> None:
    """Celda compuesta solo de espacios en columna obligatoria genera hallazgo vacio_obligatorio."""
    esquema = _esquema_vacios(["nombre"], [True])
    filas = [_fila(2, nombre="   ")]

    hallazgos = verificar_vacios(filas, esquema)

    assert len(hallazgos) == 1
    h = hallazgos[0]
    assert h.regla == "vacio_obligatorio"
    assert h.fila == 2
    assert h.columna == "nombre"


def test_req_5_1_vacio_no_genera_tipo_invalido() -> None:
    """Celda vacia en columna obligatoria no genera hallazgo tipo_invalido (separacion de Regla 2 y Regla 3)."""
    esquema = _esquema_vacios(["cantidad"], [True])
    # Reemplazamos tipo por entero para que verificar_tipos tenga algo que revisar
    esquema_entero = Esquema(
        columnas=(ColumnaEsquema(nombre="cantidad", tipo="entero", obligatoria=True),),
        clave_unica=(),
        delimitador=",",
    )
    filas = [_fila(2, cantidad="")]

    hallazgos_tipo = verificar_tipos(filas, esquema_entero)

    assert all(h.regla != "tipo_invalido" for h in hallazgos_tipo), (
        "verificar_tipos no debe generar tipo_invalido para celdas vacias"
    )
    assert hallazgos_tipo == []


def test_req_5_2_vacio_en_no_obligatoria_ignorado() -> None:
    """Celda vacia en columna no obligatoria no genera ningun hallazgo."""
    esquema = _esquema_vacios(["observacion"], [False])
    filas = [_fila(2, observacion="")]

    hallazgos = verificar_vacios(filas, esquema)

    assert hallazgos == []


# ---------------------------------------------------------------------------
# Tarea 5.3 — tests de ejemplo para verificar_tipos
# ---------------------------------------------------------------------------

from validador.lector import FilaCSV
from validador.reglas import verificar_tipos


def _fila(numero: int, **campos: str) -> FilaCSV:
    """Construye un FilaCSV con campos arbitrarios para tests."""
    return FilaCSV(numero=numero, campos=campos)


def _esquema_tipos(
    *cols: tuple,
) -> Esquema:
    """Construye un Esquema a partir de tuplas (nombre, tipo, obligatoria, formato).

    El cuarto elemento (formato) es opcional; se usa None si no se pasa.
    """
    columnas = tuple(
        ColumnaEsquema(
            nombre=col[0],
            tipo=col[1],
            obligatoria=col[2],
            formato=col[3] if len(col) > 3 else None,
        )
        for col in cols
    )
    return Esquema(columnas=columnas, clave_unica=(), delimitador=",")


def test_req_4_1_tipo_invalido_genera_hallazgo() -> None:
    """Un valor no convertible al tipo del esquema genera exactamente 1 hallazgo tipo_invalido."""
    esquema = _esquema_tipos(("cantidad", "entero", True))
    filas = [_fila(2, cantidad="abc")]

    hallazgos = verificar_tipos(filas, esquema)

    assert len(hallazgos) == 1
    assert hallazgos[0].regla == "tipo_invalido"
    assert hallazgos[0].fila == 2
    assert hallazgos[0].columna == "cantidad"
    assert hallazgos[0].valor == "abc"


def test_req_4_2_entero_valido() -> None:
    """Valores enteros validos ('10', '-3', '0') no generan hallazgo."""
    esquema = _esquema_tipos(("cantidad", "entero", True))
    filas = [
        _fila(2, cantidad="10"),
        _fila(3, cantidad="-3"),
        _fila(4, cantidad="0"),
    ]

    hallazgos = verificar_tipos(filas, esquema)

    assert hallazgos == []


def test_req_4_2_entero_con_decimal_invalido() -> None:
    """El valor '10.0' no es un entero valido y genera un hallazgo tipo_invalido."""
    esquema = _esquema_tipos(("cantidad", "entero", True))
    filas = [_fila(2, cantidad="10.0")]

    hallazgos = verificar_tipos(filas, esquema)

    assert len(hallazgos) == 1
    assert hallazgos[0].regla == "tipo_invalido"
    assert hallazgos[0].valor == "10.0"


def test_req_4_2_entero_con_espacio_invalido() -> None:
    """El valor ' 10' (con espacio inicial) no es un entero valido y genera hallazgo."""
    esquema = _esquema_tipos(("cantidad", "entero", True))
    filas = [_fila(2, cantidad=" 10")]

    hallazgos = verificar_tipos(filas, esquema)

    assert len(hallazgos) == 1
    assert hallazgos[0].regla == "tipo_invalido"
    assert hallazgos[0].valor == " 10"


def test_req_4_3_decimal_valido() -> None:
    """Valores decimales validos ('15000.50', '8200', '-3.5') no generan hallazgo."""
    esquema = _esquema_tipos(("precio", "decimal", True))
    filas = [
        _fila(2, precio="15000.50"),
        _fila(3, precio="8200"),
        _fila(4, precio="-3.5"),
    ]

    hallazgos = verificar_tipos(filas, esquema)

    assert hallazgos == []


def test_req_4_3_decimal_con_coma_invalido() -> None:
    """El valor '15.000,50' usa coma decimal y genera un hallazgo tipo_invalido."""
    esquema = _esquema_tipos(("precio", "decimal", True))
    filas = [_fila(2, precio="15.000,50")]

    hallazgos = verificar_tipos(filas, esquema)

    assert len(hallazgos) == 1
    assert hallazgos[0].regla == "tipo_invalido"
    assert hallazgos[0].valor == "15.000,50"


def test_req_4_4_fecha_valida() -> None:
    """Un valor que coincide con el formato de fecha no genera hallazgo."""
    esquema = _esquema_tipos(("fecha", "fecha", True, "%Y-%m-%d"))
    filas = [_fila(2, fecha="2026-01-15")]

    hallazgos = verificar_tipos(filas, esquema)

    assert hallazgos == []


def test_req_4_4_fecha_formato_invalido() -> None:
    """El valor '2026/09/02' no coincide con '%Y-%m-%d' y genera hallazgo tipo_invalido."""
    esquema = _esquema_tipos(("fecha", "fecha", True, "%Y-%m-%d"))
    filas = [_fila(2, fecha="2026/09/02")]

    hallazgos = verificar_tipos(filas, esquema)

    assert len(hallazgos) == 1
    assert hallazgos[0].regla == "tipo_invalido"
    assert hallazgos[0].fila == 2
    assert hallazgos[0].columna == "fecha"
    assert hallazgos[0].valor == "2026/09/02"


def test_req_4_5_texto_siempre_valido() -> None:
    """Cualquier cadena no vacia en columna de tipo texto no genera hallazgo."""
    esquema = _esquema_tipos(("descripcion", "texto", True))
    filas = [
        _fila(2, descripcion="Hola mundo"),
        _fila(3, descripcion="123"),
        _fila(4, descripcion="@#$%"),
        _fila(5, descripcion="texto con espacios"),
    ]

    hallazgos = verificar_tipos(filas, esquema)

    assert hallazgos == []


def test_req_4_6_celda_vacia_no_obligatoria_sin_hallazgo() -> None:
    """Celda vacia en columna no obligatoria no genera hallazgo tipo_invalido."""
    esquema = _esquema_tipos(("observacion", "entero", False))
    filas = [_fila(2, observacion="")]

    hallazgos = verificar_tipos(filas, esquema)

    # verificar_tipos no debe generar tipo_invalido para celdas vacias
    tipos_invalidos = [h for h in hallazgos if h.regla == "tipo_invalido"]
    assert tipos_invalidos == []


def test_req_4_6_celda_vacia_obligatoria_sin_tipo_invalido() -> None:
    """Celda vacia en columna obligatoria no genera hallazgo tipo_invalido (lo maneja verificar_vacios)."""
    esquema = _esquema_tipos(("cantidad", "entero", True))
    filas = [_fila(2, cantidad="")]

    hallazgos = verificar_tipos(filas, esquema)

    # Solo verificar_vacios genera vacio_obligatorio; verificar_tipos no genera tipo_invalido
    tipos_invalidos = [h for h in hallazgos if h.regla == "tipo_invalido"]
    assert tipos_invalidos == []
