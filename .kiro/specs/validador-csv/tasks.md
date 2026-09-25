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

- [ ] 5. `reglas.py` — Regla 2: validación de tipos
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

  - [ ] 5.3 Escribir tests de ejemplo en `tests/test_reglas.py`.
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

  - [ ] 5.4 Escribir property tests en `tests/test_reglas.py` usando Hypothesis.
    - `test_req_4_1_tipo_invalido_propiedad` (Property 9): celda no vacía e inválida →
      exactamente 1 hallazgo `tipo_invalido`; celda válida → 0 hallazgos.
    - `test_req_4_2_entero_propiedad` (Property 10): `_es_entero_valido` verdadero si y
      solo si cadena es entero puro sin punto ni espacios.
    - `test_req_4_3_decimal_propiedad` (Property 11): `_es_decimal_valido` verdadero si
      y solo si es número con punto y sin espacios.
    - `@settings(max_examples=200)` en cada uno.
    - _Requisitos: 4.1, 4.2, 4.3_

- [ ] 6. `reglas.py` — Regla 3: vacíos en columnas obligatorias
  - [x] 6.1 Implementar `verificar_vacios(filas, esquema) -> list[Hallazgo]` en
        `src/validador/reglas.py`.
    - Celda vacía = `str.strip() == ""`.
    - Solo genera `vacio_obligatorio`; nunca `tipo_invalido`.
    - Ignora columnas no obligatorias.
    - _Requisitos: 5.1, 5.2_

  - [ ] 6.2 Escribir tests de ejemplo en `tests/test_reglas.py`.
    - `test_req_5_1_vacio_en_obligatoria_genera_hallazgo`: celda `""` → 1 hallazgo
      `vacio_obligatorio`.
    - `test_req_5_1_espacios_en_obligatoria_genera_hallazgo`: celda `"   "` → hallazgo.
    - `test_req_5_1_vacio_no_genera_tipo_invalido`: celda vacía en obligatoria → no hay
      `tipo_invalido`.
    - `test_req_5_2_vacio_en_no_obligatoria_ignorado`: celda vacía en opcional → sin
      hallazgo.
    - _Requisitos: 5.1, 5.2_

  - [ ] 6.3 Escribir property test en `tests/test_reglas.py` usando Hypothesis.
    - `test_req_5_1_vacios_propiedad` (Property 12): fila con `K` celdas vacías en
      obligatorias → exactamente `K` hallazgos `vacio_obligatorio` y 0 `tipo_invalido`
      para esas celdas.
    - `@settings(max_examples=200)`.
    - _Requisitos: 5.1_

- [ ] 7. `reglas.py` — Regla 4: duplicados por clave única
  - [ ] 7.1 Implementar `verificar_duplicados(filas, esquema) -> list[Hallazgo]` en
        `src/validador/reglas.py`.
    - Clave = concatenación de valores de `clave_unica` separados con `|`.
    - La primera aparición no genera hallazgo; las siguientes sí.
    - Filas con algún valor vacío en la clave se omiten.
    - `mensaje` incluye el número de fila de la primera aparición.
    - _Requisitos: 6.1, 6.2, 6.3, 6.4_

  - [ ] 7.2 Escribir tests de ejemplo en `tests/test_reglas.py`.
    - `test_req_6_1_duplicado_segunda_aparicion`: 2 filas con misma clave → 1 hallazgo
      en la segunda.
    - `test_req_6_1_duplicado_tres_apariciones`: 3 filas con misma clave → 2 hallazgos.
    - `test_req_6_2_mensaje_incluye_primera_fila`: `mensaje` del hallazgo referencia la
      fila de la primera aparición.
    - `test_req_6_3_clave_compuesta_valor_concatenado`: clave de dos columnas → `valor`
      es `"v1|v2"`.
    - `test_req_6_4_clave_con_vacio_ignorada`: fila con valor vacío en la clave → sin
      hallazgo.
    - _Requisitos: 6.1, 6.2, 6.3, 6.4_

  - [ ] 7.3 Escribir property tests en `tests/test_reglas.py` usando Hypothesis.
    - `test_req_6_1_duplicados_propiedad` (Property 13): grupo de `N` filas con misma
      clave → exactamente `N - 1` hallazgos.
    - `test_req_6_2_mensaje_primera_aparicion_propiedad` (Property 14): para par
      `(f1, f2)` con `f2 > f1`, el `mensaje` del hallazgo de `f2` contiene `f1`.
    - `test_req_6_3_clave_compuesta_propiedad` (Property 15): el campo `valor` del
      hallazgo es la concatenación con `|` en el orden de `clave_unica`.
    - `@settings(max_examples=200)`.
    - _Requisitos: 6.1, 6.2, 6.3_

- [ ] 8. Checkpoint — verificar que todos los tests de reglas pasen
  - Ejecutar `python -m pytest tests/test_reglas.py tests/test_esquema.py tests/test_lector.py -v`.
  - Resolver cualquier fallo antes de continuar. Preguntar al usuario si hay dudas.

- [ ] 9. `reporte.py` — formato consola
  - [ ] 9.1 Implementar `formatear_consola(ruta_csv, total_filas, hallazgos) -> str` en
        `src/validador/reporte.py`.
    - Resumen: total de filas y recuento por tipo (omite tipos con recuento 0).
    - Detalle: una línea por hallazgo, ordenada por `fila` ascendente.
    - Sin hallazgos: incluye la línea `"Sin hallazgos"`.
    - No imprime nada; devuelve `str`.
    - _Requisitos: 7.1, 7.2, 7.3_

  - [ ] 9.2 Escribir tests de ejemplo en `tests/test_reporte.py`.
    - `test_req_7_1_resumen_incluye_total_filas`: texto contiene el número de filas.
    - `test_req_7_1_resumen_tipos_con_cero_omitidos`: tipos con recuento 0 no aparecen.
    - `test_req_7_2_detalle_ordenado_por_fila`: hallazgos desordenados → salida
      ordenada ascendente.
    - `test_req_7_3_sin_hallazgos_mensaje`: sin hallazgos → texto contiene
      `"Sin hallazgos"`.
    - _Requisitos: 7.1, 7.2, 7.3_

  - [ ] 9.3 Escribir property tests en `tests/test_reporte.py` usando Hypothesis.
    - `test_req_7_1_resumen_refleja_hallazgos_propiedad` (Property 16): recuentos en
      el texto coinciden con los de la lista; ningún tipo con recuento 0 aparece.
    - `test_req_7_2_detalle_orden_propiedad` (Property 17): para cualquier orden de
      entrada, el detalle del texto está ordenado por `fila` ascendente.
    - `@settings(max_examples=200)`.
    - _Requisitos: 7.1, 7.2_

- [ ] 10. `reporte.py` — reporte JSON
  - [ ] 10.1 Implementar `escribir_json(ruta_salida, ruta_csv, ruta_esquema, total_filas, hallazgos) -> None`
         en `src/validador/reporte.py`.
    - Estructura exacta del diseño: `archivo`, `esquema`, `total_filas`,
      `total_hallazgos`, `hallazgos`.
    - `json.dumps` con `ensure_ascii=False`; sobrescribe si existe.
    - Levanta `OSError` si el directorio destino no existe.
    - _Requisitos: 8.1, 8.3_

  - [ ] 10.2 Escribir tests de ejemplo en `tests/test_reporte.py`.
    - `test_req_8_1_json_estructura_correcta`: JSON escrito contiene todos los campos
      esperados con los valores correctos.
    - `test_req_8_1_json_hallazgos_campos`: cada objeto en `hallazgos` tiene los cinco
      campos (`fila`, `columna`, `regla`, `valor`, `mensaje`).
    - `test_req_8_2_sin_arg_no_escribe_json`: sin `--salida-json` no se genera archivo
      (se prueba a nivel CLI en la tarea 11).
    - `test_req_8_3_directorio_inexistente_error`: directorio destino no existe →
      `OSError`.
    - _Requisitos: 8.1, 8.3_

  - [ ] 10.3 Escribir property test en `tests/test_reporte.py` usando Hypothesis.
    - `test_req_8_1_json_serializacion_fiel_propiedad` (Property 18): para cualquier
      lista de hallazgos, el JSON escrito contiene exactamente esos hallazgos con los
      cinco campos y los totales correctos.
    - `@settings(max_examples=200)`.
    - _Requisitos: 8.1_

- [ ] 11. `cli.py` — interfaz de línea de comandos y coordinación
  - [ ] 11.1 Implementar `_construir_parser() -> argparse.ArgumentParser` en
         `src/validador/cli.py`.
    - Argumento posicional `ruta_csv`.
    - `--esquema` obligatorio.
    - `--salida-json` opcional.
    - `--ayuda` / `-h` manejado por argparse.
    - _Requisitos: 9.1, 9.2, 9.3_

  - [ ] 11.2 Implementar `_ejecutar_validacion(ruta_csv, ruta_esquema, ruta_salida_json) -> int`
         en `src/validador/cli.py`.
    - Orden de validación del diseño: esquema → CSV → col. faltantes → tipos + vacíos +
      duplicados → reporte.
    - Si hay col. faltantes: no ejecutar reglas 2–4.
    - Captura `OSError` y `ValueError`; imprime en `stderr`; devuelve código 2.
    - Devuelve 0 sin hallazgos, 1 con hallazgos.
    - _Requisitos: 1.1, 1.2, 1.4, 1.6, 2.1, 3.2, 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3_

  - [ ] 11.3 Implementar `main() -> None` en `src/validador/cli.py`.
    - Solo llama a `_construir_parser`, `_ejecutar_validacion` y `sys.exit`.
    - `print` y `sys.exit` únicamente aquí.
    - _Requisitos: 9.1, 9.2, 9.3_

  - [ ] 11.4 Escribir tests de integración en `tests/test_cli.py`.
    - `test_req_9_1_invocacion_correcta_codigo_0`: CSV válido → código 0.
    - `test_req_9_1_invocacion_correcta_codigo_1`: CSV con hallazgos → código 1.
    - `test_req_9_2_sin_esquema_codigo_2`: argumento `--esquema` ausente → código 2.
    - `test_req_1_1_esquema_inexistente_codigo_2`: ruta de esquema no existe → código 2.
    - `test_req_2_1_csv_inexistente_codigo_2`: ruta CSV no existe → código 2.
    - `test_req_8_2_sin_salida_json_no_genera_archivo`: sin `--salida-json` no crea
      archivo JSON.
    - `test_req_8_1_con_salida_json_crea_archivo`: `--salida-json` → archivo JSON creado.
    - `test_req_3_2_col_faltante_bloquea_otras_reglas`: col. faltante → sin hallazgos de
      tipo_invalido ni duplicado.
    - `test_req_7_3_csv_valido_imprime_sin_hallazgos`: salida stdout contiene
      `"Sin hallazgos"`.
    - _Requisitos: 1.1, 2.1, 3.2, 7.3, 7.4, 8.1, 8.2, 9.1, 9.2_

- [ ] 12. `pyproject.toml` — añadir hypothesis al grupo dev
  - [ ] 12.1 Actualizar `[project.optional-dependencies]` en `pyproject.toml` para añadir
         `"hypothesis>=6"` al grupo `dev`.
    - El grupo queda: `dev = ["pytest>=8", "hypothesis>=6"]`.
    - _Requisitos: ninguno (infraestructura de desarrollo)_

  - [ ] 12.2 Copiar los archivos de datos de prueba a `tests/datos/`.
    - `tests/datos/esquema_ventas.json` (copia de `datos/esquema_ventas.json`).
    - `tests/datos/ventas_valido.csv` (copia de `datos/ventas_valido.csv`).
    - `tests/datos/ventas_invalido.csv` (copia de `datos/ventas_invalido.csv`).
    - _Requisitos: 11.1, 11.2_

- [ ] 13. Checkpoint — suite completa
  - Ejecutar `python -m pytest -v` para confirmar que todas las pruebas unitarias y de
    propiedad pasan.
  - Resolver cualquier fallo antes de continuar. Preguntar al usuario si hay dudas.

- [ ] 14. Prueba de aceptación E2E y rendimiento
  - [ ] 14.1 Escribir `test_req_11_1_invalido_exactamente_5_hallazgos` en
         `tests/test_e2e.py`.
    - Valida `tests/datos/ventas_invalido.csv` con `tests/datos/esquema_ventas.json`.
    - Verifica exactamente 5 hallazgos con fila, columna, regla y valor esperados:
      - Fila 3, `fecha`, `tipo_invalido`, `"2026/09/02"`
      - Fila 3, `cantidad`, `tipo_invalido`, `"diez"`
      - Fila 4, `id_venta`, `duplicado`, `"2"`
      - Fila 4, `cliente`, `vacio_obligatorio`, `""`
      - Fila 5, `valor_unitario`, `vacio_obligatorio`, `""`
    - _Requisitos: 11.1_

  - [ ] 14.2 Escribir `test_req_11_2_valido_cero_hallazgos` en `tests/test_e2e.py`.
    - Valida `tests/datos/ventas_valido.csv` con `tests/datos/esquema_ventas.json`.
    - Verifica 0 hallazgos y código de salida 0 (vacíos en `observacion` no son
      hallazgos porque la columna no es obligatoria).
    - _Requisitos: 11.2_

  - [ ] 14.3 Escribir `test_req_10_1_rendimiento_100k_filas` en `tests/test_e2e.py`.
    - Genera un CSV de 100 000 filas válidas con `tmp_path` y lo valida.
    - Mide con `time.perf_counter`; falla si supera 10 segundos.
    - _Requisitos: 10.1_

- [ ] 15. Checkpoint final — suite E2E y cobertura completa
  - Ejecutar `python -m pytest -v` para confirmar que toda la suite pasa, incluidos
    los tests E2E y de rendimiento.
  - Confirmar que `python -m validador datos/ventas_valido.csv --esquema datos/esquema_ventas.json`
    termina con código 0 y mensaje `"Sin hallazgos"`.
  - Preguntar al usuario si desea revisión adicional antes de cerrar.

---

## Notes

- Todas las tareas de prueba son obligatorias (no opcionales). Implementarlas junto a la
  lógica que verifican.
- `hypothesis>=6` se necesita para los property tests; añadirlo en la tarea 12 antes de
  ejecutar la suite completa.
- Los identificadores de Python siguen la norma del proyecto: sin tildes ni eñes
  (`anio`, `validar_tipos`).
- `print` y `sys.exit` solo en `cli.py`; los demás módulos propagan excepciones.
- Numeración de filas siempre en convención Excel: cabecera = fila 1, primer dato = fila 2.
- El orden de validación en `cli.py` es determinista: columnas faltantes bloquean las
  demás reglas (Requisito 3.2).

---

## Task Dependency Graph

```json
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
```
