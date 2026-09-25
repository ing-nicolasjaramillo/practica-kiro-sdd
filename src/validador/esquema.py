"""Carga y validacion del esquema JSON para el validador CSV."""

from dataclasses import dataclass
from typing import Optional


TIPOS_VALIDOS: frozenset[str] = frozenset({"entero", "decimal", "fecha", "texto"})
FORMATO_FECHA_DEFAULT: str = "%Y-%m-%d"
DELIMITADOR_DEFAULT: str = ","


@dataclass(frozen=True)
class ColumnaEsquema:
    """Representa la definicion de una columna en el esquema JSON.

    Atributos:
        nombre: Nombre exacto de la columna tal como aparece en la cabecera del CSV.
        tipo: Tipo esperado del valor. Uno de 'entero', 'decimal', 'fecha' o 'texto'.
        obligatoria: Indica si la columna es obligatoria en el CSV.
        formato: Formato de fecha para columnas de tipo 'fecha'. Si no se especifica
                 en el esquema, se usa FORMATO_FECHA_DEFAULT ('%Y-%m-%d').
    """

    nombre: str
    tipo: str
    obligatoria: bool
    formato: Optional[str] = None


@dataclass(frozen=True)
class Esquema:
    """Representa el esquema completo de validacion de un CSV.

    Atributos:
        columnas: Tupla de definiciones de columna del esquema.
        clave_unica: Tupla de nombres de columna que forman la clave unica.
                     Tupla vacia si el esquema no define clave unica.
        delimitador: Caracter separador de campos del CSV. Por defecto ','.
    """

    columnas: tuple[ColumnaEsquema, ...]
    clave_unica: tuple[str, ...]
    delimitador: str


def _validar_columna(datos: dict) -> ColumnaEsquema:
    """Valida y construye una ColumnaEsquema desde un dict JSON.

    Levanta ValueError si el tipo es desconocido o no pertenece
    al conjunto de tipos validos {'entero', 'decimal', 'fecha', 'texto'}.
    """
    tipo = datos.get("tipo", "")
    if tipo not in TIPOS_VALIDOS:
        nombre = datos.get("nombre", "<sin nombre>")
        raise ValueError(
            f"Tipo desconocido '{tipo}' en columna '{nombre}'. "
            f"Tipos validos: {sorted(TIPOS_VALIDOS)}"
        )

    formato: Optional[str] = None
    if tipo == "fecha":
        formato = datos.get("formato", FORMATO_FECHA_DEFAULT)

    return ColumnaEsquema(
        nombre=datos.get("nombre", ""),
        tipo=tipo,
        obligatoria=bool(datos.get("obligatoria", False)),
        formato=formato,
    )


def cargar_esquema(ruta: str) -> Esquema:
    """Carga y valida el esquema JSON en la ruta indicada.

    Levanta OSError si el archivo no existe o no puede leerse.
    Levanta ValueError si el JSON esta mal formado, falta el campo 'columnas',
    o algun tipo de columna no pertenece a {'entero', 'decimal', 'fecha', 'texto'}.
    """
    import json

    try:
        with open(ruta, encoding="utf-8-sig") as archivo:
            contenido = archivo.read()
    except OSError as exc:
        raise OSError(f"Error al leer el esquema '{ruta}': {exc}") from exc

    try:
        datos = json.loads(contenido)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"El esquema '{ruta}' contiene JSON mal formado: {exc}"
        ) from exc

    if "columnas" not in datos:
        raise ValueError(
            f"El esquema '{ruta}' no contiene el campo obligatorio 'columnas'."
        )

    columnas = tuple(_validar_columna(col) for col in datos["columnas"])

    clave_unica: tuple[str, ...] = tuple(datos.get("clave_unica", []))
    delimitador: str = datos.get("delimitador", DELIMITADOR_DEFAULT)

    return Esquema(
        columnas=columnas,
        clave_unica=clave_unica,
        delimitador=delimitador,
    )
