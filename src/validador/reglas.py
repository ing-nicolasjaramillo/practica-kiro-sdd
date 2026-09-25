"""Reglas de validación para el validador-csv.

Este módulo contiene el modelo de datos central (Hallazgo) y las funciones
puras de validación. Ninguna función hace I/O ni llama a sys.exit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from validador.lector import FilaCSV

if TYPE_CHECKING:
    from validador.esquema import Esquema


@dataclass(frozen=True)
class Hallazgo:
    """Representa un incumplimiento de una regla de validación en una celda concreta.

    Campos:
        fila:    Número de fila en convención Excel (cabecera=1, primer dato=2).
        columna: Nombre de la columna afectada.
        regla:   Identificador de la regla incumplida. Valores posibles:
                 "columna_faltante" | "tipo_invalido" | "vacio_obligatorio" | "duplicado".
        valor:   Valor encontrado en la celda (cadena vacía si no aplica).
        mensaje: Descripción legible del problema detectado.
    """

    fila: int
    columna: str
    regla: str
    valor: str
    mensaje: str


def verificar_columnas_faltantes(
    cabecera: list[str],
    esquema: "Esquema",
) -> list[Hallazgo]:
    """Regla 1: detecta columnas obligatorias ausentes en la cabecera del CSV.

    Compara la cabecera recibida con las columnas marcadas como obligatorias en
    el esquema. La comparación es sensible a mayusculas y minusculas.

    Argumentos:
        cabecera: Lista de nombres de columna tal como aparecen en la fila 1 del CSV.
        esquema:  Esquema cargado con la definicion de columnas y su obligatoriedad.

    Retorna:
        Lista de Hallazgo, uno por cada columna obligatoria del esquema que no
        aparece en la cabecera. Cada hallazgo tiene fila=1, valor="" y
        regla="columna_faltante". Devuelve lista vacia si no hay columnas faltantes.
    """
    cabecera_set = set(cabecera)
    hallazgos: list[Hallazgo] = []

    for columna in esquema.columnas:
        if columna.obligatoria and columna.nombre not in cabecera_set:
            hallazgos.append(
                Hallazgo(
                    fila=1,
                    columna=columna.nombre,
                    regla="columna_faltante",
                    valor="",
                    mensaje=f"La columna obligatoria '{columna.nombre}' no esta presente en la cabecera del CSV.",
                )
            )

    return hallazgos


def _es_entero_valido(valor: str) -> bool:
    """Devuelve True si la cadena representa un entero puro sin decimales ni espacios.

    Acepta: "10", "-3", "0".
    Rechaza: "10.0", " 10", "diez", "".
    """
    return bool(re.fullmatch(r"-?\d+", valor))


def _es_decimal_valido(valor: str) -> bool:
    """Devuelve True si la cadena representa un numero con punto decimal y sin espacios.

    Acepta: "15000.50", "8200", "-3.5".
    Rechaza: "15.000,50", " 3.5", "", "Inf", "NaN", "+3.5", ".5", "5.", "1e5".

    La validacion combina dos pasos:

    1. Nucleo numerico: decimal.Decimal convierte la cadena. Si no es un numero
       lanza InvalidOperation y se devuelve False. Los valores no finitos
       ("Inf", "Infinity", "NaN") si los parsea, asi que se descartan con
       is_finite(), porque el criterio 4.3 no los acepta.
    2. Guarda de forma: Decimal por si solo admite espacios alrededor, signo
       mas, parte entera o decimal omitidas y notacion con exponente; la
       expresion regular exige el patron -?digitos(.digitos)? del criterio 4.3
       (punto como separador, sin espacios, sin coma, sin exponente).
    """
    try:
        numero = Decimal(valor)
    except InvalidOperation:
        return False
    if not numero.is_finite():
        return False
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", valor))


def _es_fecha_valida(valor: str, formato: str) -> bool:
    """Devuelve True si la cadena coincide exactamente con el formato de fecha indicado.

    Usa datetime.strptime, que lanza ValueError si la cadena no se puede parsear
    completamente con el formato dado (sin caracteres sobrantes).

    Argumentos:
        valor:   Cadena a validar.
        formato: Formato de fecha en notacion de strptime, p. ej. "%Y-%m-%d".
    """
    try:
        datetime.strptime(valor, formato)
        return True
    except ValueError:
        return False


def verificar_tipos(
    filas: list[FilaCSV],
    esquema: "Esquema",
) -> list[Hallazgo]:
    """Regla 2: detecta valores con tipo incorrecto en columnas presentes.

    Para cada celda no vacia cuyo tipo no coincide con el esquema, genera un hallazgo
    de tipo 'tipo_invalido'. Las celdas vacias (obligatorias o no) se omiten; eso lo
    maneja verificar_vacios. Solo procesa columnas definidas en el esquema que existen
    en el dict de campos de la fila.

    Argumentos:
        filas:   Lista de FilaCSV con los datos del CSV.
        esquema: Esquema cargado con la definicion de columnas y sus tipos.

    Retorna:
        Lista de Hallazgo con regla='tipo_invalido' para cada celda no vacia cuyo
        valor no puede convertirse al tipo definido en el esquema. Devuelve lista
        vacia si todos los valores son validos.
    """
    col_por_nombre = {col.nombre: col for col in esquema.columnas}
    hallazgos: list[Hallazgo] = []

    for fila in filas:
        for nombre_col, valor in fila.campos.items():
            if nombre_col not in col_por_nombre:
                continue  # columna extra no definida en el esquema, ignorar
            columna = col_por_nombre[nombre_col]
            if not valor.strip():  # celda vacia → la maneja verificar_vacios
                continue

            valido = True
            if columna.tipo == "entero":
                valido = _es_entero_valido(valor)
            elif columna.tipo == "decimal":
                valido = _es_decimal_valido(valor)
            elif columna.tipo == "fecha":
                valido = _es_fecha_valida(valor, columna.formato or "%Y-%m-%d")
            # tipo "texto" siempre es valido; valido permanece True

            if not valido:
                hallazgos.append(
                    Hallazgo(
                        fila=fila.numero,
                        columna=nombre_col,
                        regla="tipo_invalido",
                        valor=valor,
                        mensaje=(
                            f"El valor '{valor}' no es de tipo '{columna.tipo}' "
                            f"esperado en la columna '{nombre_col}'."
                        ),
                    )
                )

    return hallazgos


def verificar_vacios(
    filas: list[FilaCSV],
    esquema: "Esquema",
) -> list[Hallazgo]:
    """Regla 3: detecta celdas vacias en columnas obligatorias.

    Una celda se considera vacia si su valor es la cadena vacia o compuesta solo de
    espacios (str.strip() == ""). Solo genera hallazgos de tipo 'vacio_obligatorio';
    nunca 'tipo_invalido'. Ignora columnas no obligatorias.

    Argumentos:
        filas:   Lista de FilaCSV con numeracion Excel (primer dato = fila 2).
        esquema: Esquema cargado con la definicion de columnas y su obligatoriedad.

    Retorna:
        Lista de Hallazgo, uno por cada celda vacia en columna obligatoria.
        Devuelve lista vacia si no hay celdas vacias en columnas obligatorias.
    """
    cols_obligatorias = {col.nombre for col in esquema.columnas if col.obligatoria}
    hallazgos: list[Hallazgo] = []

    for fila in filas:
        for nombre_col, valor in fila.campos.items():
            if nombre_col not in cols_obligatorias:
                continue
            if valor.strip() == "":
                hallazgos.append(
                    Hallazgo(
                        fila=fila.numero,
                        columna=nombre_col,
                        regla="vacio_obligatorio",
                        valor="",
                        mensaje=f"La columna obligatoria '{nombre_col}' tiene un valor vacio en la fila {fila.numero}.",
                    )
                )

    return hallazgos
