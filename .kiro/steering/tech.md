---
inclusion: always
---
# Tecnología y estándares

## Stack
- Python 3.11 o superior.
- Código de producción solo con biblioteca estándar: csv, json, argparse,
  datetime, decimal, dataclasses, pathlib, sys.
- pytest como única dependencia de desarrollo.
- Ninguna dependencia nueva sin aprobación explícita del usuario.

## Comandos (Windows, PowerShell, entorno virtual activo)
- Instalar: python -m pip install -e ".[dev]"
- Pruebas: python -m pytest
- Una prueba: python -m pytest tests/test_reglas.py -k req_4_1
- CLI: python -m validador datos/ventas_valido.csv --esquema datos/esquema_ventas.json

## Estándares de código
- Type hints en todas las funciones públicas.
- Docstring en español en funciones públicas.
- Identificadores en español sin tildes ni ñ (validar_tipos, anio).
- Reglas de validación como funciones puras: reciben datos, devuelven hallazgos.
- Sin print ni sys.exit fuera de cli.py.
- Hallazgos modelados como dataclass inmutable (frozen=True).
- Prohibido el except genérico silencioso. Los errores de archivo se convierten
  en un mensaje claro y código de salida 2.

## Datos y codificación
- Leer CSV con encoding="utf-8-sig" (Excel agrega BOM).
- Delimitador configurable en el esquema; por defecto ",".
- Decimales con punto en v1.
- Numeración de filas como en Excel: cabecera = fila 1, primer dato = fila 2.

## Pruebas
- TDD: la prueba se escribe antes que el código.
- Cada criterio de aceptación tiene al menos una prueba llamada
  test_req_<requisito>_<criterio>_<caso>. Ej: test_req_4_2_fecha_formato_invalido.
- Datos pequeños en tests/datos/; los grandes se generan con tmp_path.
- Ninguna prueba depende de red ni de rutas absolutas.