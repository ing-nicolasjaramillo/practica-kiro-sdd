import os
import subprocess
import sys
from pathlib import Path


def test_req_11_1_invalido_exactamente_5_hallazgos():
    """Comprueba los hallazgos del CSV invalido al ejecutar la CLI real."""
    raiz = Path(__file__).resolve().parents[1]
    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "validador",
            "datos/ventas_invalido.csv",
            "--esquema",
            "datos/esquema_ventas.json",
        ],
        cwd=raiz,
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                [str(raiz / "src"), os.environ.get("PYTHONPATH", "")]
            ),
        },
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    hallazgos = []
    for linea in resultado.stdout.splitlines():
        if linea.startswith("fila: "):
            campos = dict(
                campo.split(": ", maxsplit=1)
                for campo in linea.split(" | ")
                if ": " in campo
            )
            hallazgos.append(
                (
                    int(campos["fila"]),
                    campos["columna"],
                    campos["regla"],
                    campos["valor"],
                )
            )

    assert resultado.returncode == 1
    assert sorted(hallazgos) == sorted([
        (3, "fecha", "tipo_invalido", "2026/09/02"),
        (3, "cantidad", "tipo_invalido", "diez"),
        (4, "id_venta", "duplicado", "2"),
        (4, "cliente", "vacio_obligatorio", ""),
        (5, "valor_unitario", "vacio_obligatorio", ""),
    ])
