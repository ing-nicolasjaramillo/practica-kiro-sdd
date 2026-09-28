import json

from validador.reglas import Hallazgo
from validador.reporte import escribir_json, formatear_consola


def test_req_7_2_detalle_ordenado_por_fila():
    hallazgos = [
        Hallazgo(5, "nombre", "tipo_invalido", "123", "Tipo incorrecto"),
        Hallazgo(2, "fecha", "tipo_invalido", "2026/09/02", "Fecha incorrecta"),
    ]

    reporte = formatear_consola("ventas.csv", 6, hallazgos)
    lineas_detalle = [linea for linea in reporte.splitlines() if "fila:" in linea]

    assert len(lineas_detalle) == 2
    assert "fila: 2" in lineas_detalle[0]
    assert "columna: fecha" in lineas_detalle[0]
    assert "regla: tipo_invalido" in lineas_detalle[0]
    assert "valor: 2026/09/02" in lineas_detalle[0]
    assert "mensaje: Fecha incorrecta" in lineas_detalle[0]
    assert "fila: 5" in lineas_detalle[1]
    assert (
        lineas_detalle[0].index("fila:")
        < lineas_detalle[0].index("columna:")
        < lineas_detalle[0].index("regla:")
        < lineas_detalle[0].index("valor:")
        < lineas_detalle[0].index("mensaje:")
    )


def test_req_7_3_sin_hallazgos_mensaje():
    reporte = formatear_consola("ventas.csv", 3, [])

    assert "Sin hallazgos" in reporte


def test_req_8_1_json_estructura_correcta(tmp_path):
    ruta_salida = tmp_path / "reporte.json"
    hallazgos = [
        Hallazgo(3, "fecha", "tipo_invalido", "2026/09/02", "Fecha inválida"),
        Hallazgo(4, "cliente", "vacio_obligatorio", "", "Campo obligatorio vacío"),
    ]

    escribir_json(str(ruta_salida), "ventas.csv", "esquema.json", 5, hallazgos)

    contenido = ruta_salida.read_text(encoding="utf-8")
    assert "inválida" in contenido
    assert json.loads(contenido) == {
        "archivo": "ventas.csv",
        "esquema": "esquema.json",
        "total_filas": 5,
        "total_hallazgos": 2,
        "hallazgos": [
            {
                "fila": 3,
                "columna": "fecha",
                "regla": "tipo_invalido",
                "valor": "2026/09/02",
                "mensaje": "Fecha inválida",
            },
            {
                "fila": 4,
                "columna": "cliente",
                "regla": "vacio_obligatorio",
                "valor": "",
                "mensaje": "Campo obligatorio vacío",
            },
        ],
    }
