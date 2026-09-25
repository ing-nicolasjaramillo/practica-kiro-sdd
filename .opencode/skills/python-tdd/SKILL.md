---
name: python-tdd
description: Ciclo TDD con pytest para el proyecto validador-csv. Úsala siempre que vayas a crear o modificar código en src/validador/.
---
# Ciclo TDD

## 1. Rojo
- Por cada criterio EARS de la tarea, escribe una prueba en tests/test_<modulo>.py.
- Nombre: test_req_<requisito>_<criterio>_<caso>.
  Ejemplo: test_req_6_2_duplicado_indica_primera_fila.
- Estructura Arrange / Act / Assert, con una sola razón para fallar.
- Ejecuta python -m pytest -q <archivo> y confirma que FALLA por la razón
  esperada (AssertionError o función inexistente), no por un error de sintaxis.

## 2. Verde
- Escribe el mínimo código que haga pasar la prueba.
- Respeta tech.md: type hints, docstring en español, funciones puras,
  sin print fuera de cli.py.

## 3. Refactor
- Mejora nombres y elimina duplicación sin cambiar comportamiento.
- Ejecuta la suite completa: python -m pytest -q. Debe quedar en verde.

## Patrones útiles
Archivo temporal:
```python
def test_req_3_1_columna_obligatoria_faltante(tmp_path):
    archivo = tmp_path / "ventas.csv"
    archivo.write_text("id_venta,fecha\n1,2026-09-01\n", encoding="utf-8")
    # Act y Assert según el criterio
```
Varios casos del mismo criterio: @pytest.mark.parametrize.
CLI: llama main(argv) directamente, verifica el código de salida y captura
la salida con el fixture capsys.

## Prohibido
- Escribir el código antes que la prueba.
- Pruebas sin assert o con assert True.
- Probar detalles internos en lugar del comportamiento que pide el criterio.
