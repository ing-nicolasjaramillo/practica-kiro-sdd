import json

import pytest

from validador.cli import main


def test_req_9_1_csv_valido_codigo_0(tmp_path, capsys):
    archivo_csv = tmp_path / "ventas.csv"
    archivo_esquema = tmp_path / "esquema.json"
    archivo_csv.write_text("id,nombre\n1,Ana\n", encoding="utf-8")
    archivo_esquema.write_text(
        json.dumps(
            {
                "columnas": [
                    {"nombre": "id", "tipo": "entero", "obligatoria": True},
                    {"nombre": "nombre", "tipo": "texto", "obligatoria": True},
                ],
                "clave_unica": ["id"],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as resultado:
        main([str(archivo_csv), "--esquema", str(archivo_esquema)])

    assert resultado.value.code == 0
    assert "Sin hallazgos" in capsys.readouterr().out


def test_req_2_1_csv_inexistente_codigo_2(tmp_path, capsys):
    ruta_csv = tmp_path / "no-existe.csv"
    archivo_esquema = tmp_path / "esquema.json"
    archivo_esquema.write_text(
        json.dumps({"columnas": [{"nombre": "id", "tipo": "entero", "obligatoria": True}]}),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as resultado:
        main([str(ruta_csv), "--esquema", str(archivo_esquema)])

    salida = capsys.readouterr()
    assert resultado.value.code == 2
    assert str(ruta_csv) in salida.err
