"""Modulo de lectura de archivos CSV para el validador."""

import csv
from dataclasses import dataclass


@dataclass(frozen=True)
class FilaCSV:
    """Representa una fila del CSV con su numero de fila (convencion Excel) y sus campos."""

    numero: int           # Numeracion Excel: cabecera=1, primer dato=2
    campos: dict[str, str]  # {nombre_columna: valor_celda}


def leer_csv(ruta: str, delimitador: str) -> tuple[list[str], list[FilaCSV]]:
    """Lee el CSV y devuelve (cabecera, filas).

    cabecera: lista de nombres de columna tal como aparecen en la fila 1.
    filas: lista de FilaCSV con numeracion Excel (primer dato = fila 2).

    Lee con encoding='utf-8-sig' para eliminar el BOM de Excel automaticamente.
    Levanta OSError si el archivo no existe o no puede leerse.
    Devuelve (cabecera, []) si el CSV no contiene filas de datos.
    """
    try:
        with open(ruta, encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo, delimiter=delimitador)
            cabecera: list[str] = list(lector.fieldnames or [])
            filas: list[FilaCSV] = [
                FilaCSV(numero=i + 2, campos=dict(fila))
                for i, fila in enumerate(lector)
            ]
    except FileNotFoundError as exc:
        raise OSError(f"No se encontro el archivo CSV: {ruta}") from exc
    except OSError as exc:
        raise OSError(f"Error al leer el archivo CSV: {ruta}: {exc}") from exc

    return cabecera, filas
