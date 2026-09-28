"""Formato de reportes de validación para consola y JSON."""

import json
from pathlib import Path

from validador.reglas import Hallazgo


TIPOS_REGLA_ORDEN = [
    "columna_faltante",
    "tipo_invalido",
    "vacio_obligatorio",
    "duplicado",
]


def formatear_consola(
    ruta_csv: str, total_filas: int, hallazgos: list[Hallazgo]
) -> str:
    """Devuelve el reporte de consola con resumen y detalle ordenado por fila."""
    lineas = [f"Archivo: {ruta_csv}", f"Total de filas: {total_filas}"]
    recuentos = {regla: 0 for regla in TIPOS_REGLA_ORDEN}
    for hallazgo in hallazgos:
        recuentos[hallazgo.regla] = recuentos.get(hallazgo.regla, 0) + 1

    reglas_con_hallazgos = [
        regla for regla in TIPOS_REGLA_ORDEN if recuentos.get(regla, 0) > 0
    ]
    reglas_adicionales = sorted(
        regla
        for regla, recuento in recuentos.items()
        if regla not in TIPOS_REGLA_ORDEN and recuento > 0
    )
    for regla in reglas_con_hallazgos + reglas_adicionales:
        lineas.append(f"{regla}: {recuentos[regla]}")

    if not hallazgos:
        lineas.append("Sin hallazgos")
    else:
        lineas.append("Detalle:")
        for hallazgo in sorted(hallazgos, key=lambda item: item.fila):
            lineas.append(
                f"fila: {hallazgo.fila} | columna: {hallazgo.columna} | "
                f"regla: {hallazgo.regla} | valor: {hallazgo.valor} | "
                f"mensaje: {hallazgo.mensaje}"
            )

    return "\n".join(lineas)


def escribir_json(
    ruta_salida: str,
    ruta_csv: str,
    ruta_esquema: str,
    total_filas: int,
    hallazgos: list[Hallazgo],
) -> None:
    """Escribe el reporte JSON, sobrescribiendo el destino si ya existe."""
    reporte = {
        "archivo": ruta_csv,
        "esquema": ruta_esquema,
        "total_filas": total_filas,
        "total_hallazgos": len(hallazgos),
        "hallazgos": [
            {
                "fila": hallazgo.fila,
                "columna": hallazgo.columna,
                "regla": hallazgo.regla,
                "valor": hallazgo.valor,
                "mensaje": hallazgo.mensaje,
            }
            for hallazgo in hallazgos
        ],
    }
    Path(ruta_salida).write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8"
    )
