# Implementation Plan: validador-csv

## Overview

Implementación incremental del validador-csv en Python 3.11, usando únicamente la
biblioteca estándar en producción y pytest + hypothesis en desarrollo. Cada tarea produce
código ejecutable o tests ejecutables antes de pasar a la siguiente.

---

## Tasks

- [x] 1. Setup del paquete y modelo central `Hallazgo`
  - [x] 1.1 Actualizar `src/validador/__init__.py` con la versión del paquete y crear
        `src/validador/__main__.py` con el stub `from validador.cli import main`.
    - Dejar `__init__.py` con solo `__version__ = "0.1.0"`.
    - `__main__.py` ejecuta `main()` dentro del bloque `if __name__ == "__main__"`.
    - _Requisitos: 9.1_

  - [x] 1.2 Definir el dataclass inmutable `Hallazgo` en `src/validador/reglas.py`
        (campos: `fila: int`, `columna: str`, `regla: str`, `valor: str`, `mensaje: str`).
    - Usar `@dataclass(frozen=True)`.
    - Añadir docstring en español.
    - _Requisitos: 3.1, 4.1, 5.1, 6.1_

  - [x] 1.3 Escribir tests de construcción e inmutabilidad del dataclass `Hallazgo`
        en `tests/test_reglas.py`.
    - `test_req_0_hallazgo_construccion_correcta`: verifica que los cinco campos se
      asignan bien.
    - `test_req_0_hallazgo_es_inmutable`: verifica que asignar un campo lanza
      `FrozenInstanceError`.
    - _Requisitos: 3.1 (modelo de datos)_

- [x] 2. `esquema.py` — carga y validación del esquema JSON
  - [x] 2.1 Implementar los dataclasses `ColumnaEsquema` y `Esquema` en
        `src/validador/esquema.py` (exactamente como en el diseño).
    - Constantes `TIPOS_VALIDOS`, `FORMATO_FECHA_DEFAULT`, `DELIMITADOR_DEFAULT`.
    - _Requisitos: 1.3, 1.4, 1.5_

  - [x] 2.2 Implementar `_validar_columna(datos: dict) -> ColumnaEsquema` en
        `src/validador/esquema.py`.
    - Levanta `ValueError` si `tipo` no está en `TIPOS_VALIDOS`.
    - Resuelve el formato de fecha con el default si falta el campo `formato`.
    - _Requisitos: 1.4, 1.5_

  - [x] 2.3 Implementar `cargar_esquema(ruta: str) -> Esquema` en
        `src/validador/esquema.py`.
    - Levanta `OSError` si el archivo no existe.
    - Levanta `ValueError` si JSON mal formado, campo `columnas` ausente o tipo inválido.
    - Usa `clave_unica` como tupla vacía si el campo no está en el JSON.
    - _Requisitos: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [x] 2.4 Escribir tests de ejemplo en `tests/test_esquema.py`.
    - `test_req_1_1_esquema_no_existe`: archivo inexistente → `OSError`.
    - `test_req_1_2_esquema_json_malformado`: JSON roto → `ValueError`.
    - `test_req_1_3_delimitador_presente`: delimitador del esquema se respeta.
    - `test_req_1_3_delimitador_ausente`: default `","` cuando no hay campo.
    - `test_req_1_4_tipo_desconocido`: tipo `"booleano"` → `ValueError`.
    - `test_req_1_5_formato_fecha_presente`: formato personalizado se almacena.
    - `test_req_1_5_formato_fecha_ausente`: default `%Y-%m-%d` cuando no hay formato.
    - `test_req_1_6_campo_columnas_ausente`: JSON sin `columnas` → `ValueError`.
    - _Requisitos: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [x] 2.5 Escribir property tests en `tests/test_esquema.py` usando Hypothesis.
    - `test_req_1_3_delimitador_propiedad` (Property 1): para cualquier carácter `d`,
      `cargar_esquema` devuelve `Esquema` con `delimitador == d`.
    - `test_req_1_4_tipos_desconocidos_propiedad` (Property 2): para cualquier cadena
      fuera de `TIPOS_VALIDOS`, `cargar_esquema` levanta `ValueError`.
    - `@settings(max_examples=200)` en cada property test.
    - _Requisitos: 1.3, 1.4_

- [x] 3. `lector.py` — lectura del CSV
  - [x] 3.1 Implementar el dataclass `FilaCSV` y la función `leer_csv` en
        `src/validador/lector.py`.
    - `FilaCSV(frozen=True)` con campos `numero: int` y `campos: dict[str, str]`.
    - `leer_csv(ruta, delimitador)` devuelve `(list[str], list[FilaCSV])`.
    - Encoding `utf-8-sig`; numeración Excel (`numero = i + 2`).
    - Devuelve `(cabecera, [])` si no hay filas de datos.
    - Levanta `OSError` si el archivo no existe.
    - _Requisitos: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 3.2 Escribir tests de ejemplo en `tests/test_lector.py`.
    - `test_req_2_1_csv_no_existe`: archivo inexistente → `OSError`.
    - `test_req_2_2_bom_eliminado`: CSV con BOM → primer campo de cabecera sin `\ufeff`.
    - `test_req_2_3_numeracion_excel`: primer dato tiene `numero == 2`.
    - `test_req_2_4_delimitador_personalizado`: CSV con `|` leído correctamente.
    - `test_req_2_5_csv_sin_datos`: CSV solo con cabecera → lista vacía.
    - _Requisitos: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 3.3 Escribir property tests en `tests/test_lector.py` usando Hypothesis.
    - `test_req_2_3_numeracion_propiedad` (Property 3): CSV con `N` filas → lista de
      longitud `N` con `fila[i].numero == i + 2`.
    - `test_req_2_2_bom_propiedad` (Property 4): CSV con y sin BOM → misma cabecera.
    - `@settings(max_examples=200)`.
    - _Requisitos: 2.2, 2.3_

- [x] 4. `reglas.py` — Regla 1: columnas faltantes
  - [x] 4.1 Implementar `verificar_columnas_faltantes(cabecera, esquema) -> list[Hallazgo]`
        en `src/validador/reglas.py`.
    - Un `Hallazgo` por columna obligatoria ausente (`fila=1`, `valor=""`).
    - Comparación case-sensitive.
    - _Requisitos: 3.1, 3.4, 3.5_

  - [x] 4.2 Escribir tests de ejemplo en `tests/test_reglas.py`.
    - `test_req_3_1_columna_faltante_unica`: una obligatoria ausente → 1 hallazgo.
    - `test_req_3_1_columnas_faltantes_multiples`: dos ausentes → 2 hallazgos.
    - `test_req_3_3_todas_presentes`: todas las obligatorias → lista vacía.
    - `test_req_3_4_columna_extra_ignorada`: columna extra no genera hallazgo.
    - `test_req_3_5_case_sensitive`: `"Fecha"` ausente cuando esquema exige `"fecha"`.
    - _Requisitos: 3.1, 3.3, 3.4, 3.5_

  - [x] 4.3 Escribir property test en `tests/test_reglas.py` usando Hypothesis.
    - `test_req_3_1_columnas_faltantes_propiedad` (Property 5): para cualquier
      subconjunto `F` de obligatorias ausentes, se generan exactamente `|F|` hallazgos
      de tipo `columna_faltante` con `fila=1`.
    - `@settings(max_examples=200)`.
    - _Requisitos: 3.1_

- [x] 0. Reconciliación del avance de Kiro (ver auditoria.md)
- [x] 0.1 Reparar tests/test_reglas.py sin cambiar comportamiento
  - Eliminar el bloque de pruebas duplicado que queda sombreado y conservar
    una sola versión de cada prueba
  - Dejar una sola definición de _esquema_simple y de _fila, con firma única,
    y ajustar todas sus llamadas
  - Terminado cuando: python -m pytest -q da 0 fallos y 0 errores, y ningún
    nombre de prueba está repetido en el archivo
  - No se escribe código de producción ni pruebas nuevas en esta tarea
  - _Requisitos: los cubiertos por las tareas 4, 5.3 y 6.2 (sin comportamiento nuevo)_
- [x] 0.2 Ajustes de calidad en src/validador/reglas.py
  - Mover los imports al inicio del archivo
  - Reimplementar _es_decimal_valido con decimal.Decimal, como exige design.md;
    las pruebas existentes del requisito 4.3 deben seguir en verde
  - _Requisitos: 4.3_

- [x] 5. `reglas.py` — Regla 2: validación de tipos
  - [x] 5.1 Implementar las funciones privadas `_es_entero_valido`, `_es_decimal_valido`
        y `_es_fecha_valida` en `src/validador/reglas.py`.
    - `_es_entero_valido`: rechaza decimales, espacios, texto.
    - `_es_decimal_valido`: usa `decimal.Decimal`; rechaza coma y espacios.
    - `_es_fecha_valida`: usa `datetime.strptime`; falla si quedan caracteres sobrantes.
    - _Requisitos: 4.2, 4.3, 4.4_

  - [x] 5.2 Implementar `verificar_tipos(filas, esquema) -> list[Hallazgo]` en
        `src/validador/reglas.py`.
    - Omite celdas vacías (las maneja Regla 3).
    - Solo procesa columnas definidas en el esquema que existen en la fila.
    - _Requisitos: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [x] 5.3 Escribir tests de ejemplo en `tests/test_reglas.py`.
    - `test_req_4_1_tipo_invalido_genera_hallazgo`: valor no convertible → hallazgo.
    - `test_req_4_2_entero_valido`: `"10"`, `"-3"`, `"0"` no generan hallazgo.
    - `test_req_4_2_entero_con_decimal_invalido`: `"10.0"` genera hallazgo.
    - `test_req_4_2_entero_con_espacio_invalido`: `" 10"` genera hallazgo.
    - `test_req_4_3_decimal_valido`: `"15000.50"`, `"8200"`, `"-3.5"` no generan hallazgo.
    - `test_req_4_3_decimal_con_coma_invalido`: `"15.000,50"` genera hallazgo.
    - `test_req_4_4_fecha_valida`: coincide con formato → no genera hallazgo.
    - `test_req_4_4_fecha_formato_invalido`: `"2026/09/02"` con formato `%Y-%m-%d` → hallazgo.
    - `test_req_4_5_texto_siempre_valido`: cualquier cadena no vacía → no genera hallazgo.
    - `test_req_4_6_celda_vacia_no_obligatoria_sin_hallazgo`: celda vacía en opcional → sin `tipo_invalido`.
    - `test_req_4_6_celda_vacia_obligatoria_sin_tipo_invalido`: celda vacía en obligatoria → sin `tipo_invalido`.
    - _Requisitos: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [x] 5.4 Escribir property tests en `tests/test_reglas.py` usando Hypothesis.
    - `test_req_4_1_tipo_invalido_propiedad` (Property 9): celda no vacía e inválida →
      exactamente 1 hallazgo `tipo_invalido`; celda válida → 0 hallazgos.
    - `test_req_4_2_entero_propiedad` (Property 10): `_es_entero_valido` verdadero si y
      solo si cadena es entero puro sin punto ni espacios.
    - `test_req_4_3_decimal_propiedad` (Property 11): `_es_decimal_valido` verdadero si
      y solo si es número con punto y sin espacios.
    - `@settings(max_examples=200)` en cada uno.
    - _Requisitos: 4.1, 4.2, 4.3_

- [x] 6. `reglas.py` — Regla 3: vacíos en columnas obligatorias
  - [x] 6.1 Implementar `verificar_vacios(filas, esquema) -> list[Hallazgo]` en
        `src/validador/reglas.py`.
    - Celda vacía = `str.strip() == ""`.
    - Solo genera `vacio_obligatorio`; nunca `tipo_invalido`.
    - Ignora columnas no obligatorias.
    - _Requisitos: 5.1, 5.2_

  - [x] 6.2 Escribir tests de ejemplo en `tests/test_reglas.py`.
    - `test_req_5_1_vacio_en_obligatoria_genera_hallazgo`: celda `""` → 1 hallazgo
      `vacio_obligatorio`.
    - `test_req_5_1_espacios_en_obligatoria_genera_hallazgo`: celda `"   "` → hallazgo.
    - `test_req_5_1_vacio_no_genera_tipo_invalido`: celda vacía en obligatoria → no hay
      `tipo_invalido`.
    - `test_req_5_2_vacio_en_no_obligatoria_ignorado`: celda vacía en opcional → sin
      hallazgo.
    - _Requisitos: 5.1, 5.2_

  - [x] 6.3 Escribir property test en `tests/test_reglas.py` usando Hypothesis.
    - `test_req_5_1_vacios_propiedad` (Property 12): fila con `K` celdas vacías en
      obligatorias → exactamente `K` hallazgos `vacio_obligatorio` y 0 `tipo_invalido`
      para esas celdas.
    - `@settings(max_examples=200)`.
    - _Requisitos: 5.1_

- [x] 7. `reglas.py` — Regla 4: duplicados por clave única
  - [x] 7.1 Implementar `verificar_duplicados(filas, esquema) -> list[Hallazgo]`
    - Clave = valores de `clave_unica` unidos con `|`; la primera aparición no genera hallazgo.
    - Filas con algún valor vacío en la clave se omiten.
    - `mensaje` incluye la fila de la primera aparición.
    - Pruebas (3): `test_req_6_1_duplicado_segunda_aparicion`,
      `test_req_6_2_mensaje_incluye_primera_fila`, `test_req_6_4_clave_con_vacio_ignorada`.
    - _Requisitos: 6.1, 6.2, 6.4_

- [x] 8. `reporte.py` — consola y JSON
  - [x] 8.1 Implementar `formatear_consola(...) -> str` y `escribir_json(...) -> None`
    - Consola: total de filas, recuento por regla y detalle ordenado por fila;
      "Sin hallazgos" si la lista está vacía.
    - JSON: `archivo`, `esquema`, `total_filas`, `total_hallazgos`, `hallazgos`;
      `ensure_ascii=False`.
    - Pruebas (3): `test_req_7_2_detalle_ordenado_por_fila`,
      `test_req_7_3_sin_hallazgos_mensaje`, `test_req_8_1_json_estructura_correcta`.
    - _Requisitos: 7.2, 7.3, 8.1_

- [x] 9. `cli.py` — interfaz y coordinación
  - [x] 9.1 Implementar `cli.py` (parser, ejecución y `main`) según design.md
    - Orden: esquema → CSV → columnas faltantes (si hay, no se ejecutan las reglas 2–4)
      → tipos, vacíos y duplicados → reporte.
    - Códigos: 0 sin hallazgos, 1 con hallazgos, 2 ante `OSError`/`ValueError` (mensaje a stderr).
    - `print` y `sys.exit` solo en este módulo.
    - Pruebas (2) en `tests/test_cli.py`: `test_req_9_1_csv_valido_codigo_0`,
      `test_req_2_1_csv_inexistente_codigo_2`.
    - _Requisitos: 9.1, 2.1_

- [ ] 10. Aceptación y cierre
  - [x] 10.1 `test_req_11_1_invalido_exactamente_5_hallazgos` en `tests/test_e2e.py`
    - Usa `datos/ventas_invalido.csv` y `datos/esquema_ventas.json`, con rutas relativas a la raíz.
    - Verifica los 5 hallazgos esperados (fila, columna, regla, valor) y el código de salida 1.
    - _Requisitos: 11.1_
  - [ ] 10.2 Checkpoint final
    - @verificador: `python -m pytest -q` en verde.
    - Manual (lo hace el usuario): `python -m validador datos/ventas_valido.csv
      --esquema datos/esquema_ventas.json` → código 0 y "Sin hallazgos".

## Notes

- Alcance reducido por ser un laboratorio: las pruebas de propiedad llegan solo hasta
  la tarea 6, y las tareas originales 7–15 se consolidaron en 7–10.
- Criterios sin prueba dedicada (decisión consciente): 3.2, 6.3, 7.1, 7.4, 8.2, 8.3,
  9.2, 9.3, 10.1 y 11.2.
- print y sys.exit solo en cli.py; numeración de filas estilo Excel.

## Task Dependency Graph

<!-- ```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3", "2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3"] },
    { "id": 3, "tasks": ["2.4", "2.5", "3.1"] },
    { "id": 4, "tasks": ["3.2", "3.3", "4.1"] },
    { "id": 5, "tasks": ["4.2", "4.3", "5.1"] },
    { "id": 6, "tasks": ["5.2", "6.1"] },
    { "id": 7, "tasks": ["5.3", "5.4", "6.2", "6.3", "7.1"] },
    { "id": 8, "tasks": ["7.2", "7.3", "9.1"] },
    { "id": 9, "tasks": ["9.2", "9.3", "10.1"] },
    { "id": 10, "tasks": ["10.2", "10.3", "11.1"] },
    { "id": 11, "tasks": ["11.2", "12.1", "12.2"] },
    { "id": 12, "tasks": ["11.3", "11.4"] },
    { "id": 13, "tasks": ["14.1", "14.2", "14.3"] }
  ]
}
``` -->
