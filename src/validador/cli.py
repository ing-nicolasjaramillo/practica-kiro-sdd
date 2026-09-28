"""Interfaz de linea de comandos y coordinacion del validador CSV."""

import argparse
import sys

from validador.esquema import cargar_esquema
from validador.lector import leer_csv
from validador.reglas import (
    Hallazgo,
    verificar_columnas_faltantes,
    verificar_duplicados,
    verificar_tipos,
    verificar_vacios,
)
from validador.reporte import formatear_consola, escribir_json


def _construir_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos de la interfaz de linea de comandos."""
    parser = argparse.ArgumentParser(
        description="Valida un archivo CSV contra un esquema JSON.",
        add_help=False,
    )
    parser.add_argument(
        "ruta_csv",
        help="Ruta del archivo CSV que se va a validar.",
    )
    parser.add_argument(
        "--esquema",
        required=True,
        help="Ruta del archivo JSON que define el esquema.",
    )
    parser.add_argument(
        "--salida-json",
        metavar="RUTA",
        help="Ruta opcional donde guardar el reporte JSON.",
    )
    parser.add_argument(
        "-h",
        "--ayuda",
        action="help",
        help="Muestra esta descripción de los argumentos y termina.",
    )
    return parser


def _ejecutar_validacion(
    ruta_csv: str,
    ruta_esquema: str,
    ruta_salida_json: str | None,
) -> int:
    """Ejecuta la validacion y devuelve el codigo de salida correspondiente.

    Los errores de entrada o salida y los errores de validacion del esquema se
    imprimen en stderr y se convierten en el codigo de salida 2.
    """
    try:
        esquema = cargar_esquema(ruta_esquema)
        cabecera, filas = leer_csv(ruta_csv, esquema.delimitador)

        hallazgos: list[Hallazgo] = verificar_columnas_faltantes(cabecera, esquema)
        if not hallazgos:
            hallazgos.extend(verificar_tipos(filas, esquema))
            hallazgos.extend(verificar_vacios(filas, esquema))
            hallazgos.extend(verificar_duplicados(filas, esquema))

        hallazgos.sort(key=lambda hallazgo: hallazgo.fila)
        print(formatear_consola(ruta_csv, len(filas), hallazgos))

        if ruta_salida_json is not None:
            escribir_json(
                ruta_salida_json,
                ruta_csv,
                ruta_esquema,
                len(filas),
                hallazgos,
            )
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    return 1 if hallazgos else 0


def main(argv: list[str] | None = None) -> None:
    """Parsea los argumentos, valida el CSV y termina con el codigo adecuado."""
    argumentos = _construir_parser().parse_args(argv)
    codigo = _ejecutar_validacion(
        argumentos.ruta_csv,
        argumentos.esquema,
        argumentos.salida_json,
    )
    sys.exit(codigo)
