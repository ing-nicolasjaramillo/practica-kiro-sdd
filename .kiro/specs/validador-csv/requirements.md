# Requirements Document

## Introduction

El **Validador CSV** es una herramienta de línea de comandos en Python que verifica la calidad de un archivo CSV contra un esquema JSON antes de usarlo en procesos de analítica. Detecta cuatro categorías de problemas —columnas faltantes, tipos incorrectos, vacíos en columnas obligatorias y duplicados por clave única— y produce un reporte legible en consola y, opcionalmente, un reporte procesable en JSON. La herramienta usa exclusivamente la biblioteca estándar de Python 3.11.

---

## Glossary

- **CSV**: Archivo de valores separados por comas (o delimitador configurable) que contiene los datos a validar.
- **Esquema**: Archivo JSON que describe las columnas esperadas (nombre, tipo, obligatoriedad), el delimitador y la clave única del CSV.
- **Hallazgo**: Incumplimiento concreto de una regla en una fila y columna específicas, modelado como estructura inmutable con los campos: `fila`, `columna`, `regla`, `valor`, `mensaje`.
- **Regla**: Verificación atómica aplicada sobre los datos del CSV (columna faltante, tipo inválido, vacío en obligatoria, duplicado).
- **Clave unica**: Conjunto de una o más columnas del esquema cuyos valores combinados deben ser únicos en todo el CSV.
- **Fila**: Línea del CSV numerada según la convención Excel: la cabecera es la fila 1 y el primer registro de datos es la fila 2.

---

## Requirements

### Requisito 1 – Carga y validación del esquema

**Historia de usuario:** Como analista de datos, quiero que el validador detecte esquemas inválidos o inexistentes antes de procesar el CSV, para recibir un mensaje claro y poder corregir el problema.

#### Criterios de aceptación

1.1. CUANDO el archivo de esquema no existe en la ruta indicada, EL SISTEMA DEBERÁ emitir un mensaje de error que incluya la ruta indicada y terminar con código de salida 2.

1.2. CUANDO el archivo de esquema existe pero contiene JSON mal formado, EL SISTEMA DEBERÁ emitir un mensaje de error que mencione el problema de sintaxis JSON y terminar con código de salida 2.

1.3. CUANDO el esquema es válido y contiene el campo `delimitador`, EL SISTEMA DEBERÁ usar ese valor como separador de campos del CSV. CUANDO el esquema no contiene el campo `delimitador`, EL SISTEMA DEBERÁ usar la coma (`,`) como delimitador predeterminado.

1.4. CUANDO el esquema contiene una columna con un tipo distinto de `entero`, `decimal`, `fecha` o `texto`, EL SISTEMA DEBERÁ emitir un mensaje de error que identifique la columna y el tipo desconocido, y terminar con código de salida 2.

1.5. CUANDO el tipo de una columna es `fecha` y el campo `formato` está presente en esa columna, EL SISTEMA DEBERÁ usar ese formato para validar las celdas. CUANDO el campo `formato` no está presente, EL SISTEMA DEBERÁ usar `%Y-%m-%d` como formato predeterminado.

1.6. CUANDO el archivo de esquema existe y contiene JSON bien formado pero no incluye el campo `columnas`, EL SISTEMA DEBERÁ emitir un mensaje de error descriptivo y terminar con código de salida 2.

---

### Requisito 2 – Lectura del CSV

**Historia de usuario:** Como analista de datos, quiero que el validador lea correctamente el CSV exportado desde distintos sistemas, para no obtener errores espurios por problemas de codificación o de ruta.

#### Criterios de aceptación

2.1. CUANDO el archivo CSV no existe en la ruta indicada, EL SISTEMA DEBERÁ emitir un mensaje de error que incluya la ruta indicada y terminar con código de salida 2.

2.2. CUANDO el archivo CSV existe, EL SISTEMA DEBERÁ leerlo con codificación `utf-8-sig` para eliminar el BOM que agrega Excel.

2.3. CUANDO el archivo CSV existe, EL SISTEMA DEBERÁ numerar las filas comenzando en 1 para la cabecera y en 2 para el primer registro de datos, manteniendo esa numeración en todos los hallazgos y reportes.

2.4. CUANDO el archivo CSV existe, EL SISTEMA DEBERÁ usar el delimitador definido en el esquema para separar los campos de cada fila.

2.5. CUANDO el archivo CSV existe pero no contiene filas de datos (el archivo está vacío o contiene únicamente la fila de cabecera), EL SISTEMA DEBERÁ completar la validación con 0 hallazgos y terminar con código de salida 0.

---

### Requisito 3 – Regla 1: columnas obligatorias ausentes en la cabecera

**Historia de usuario:** Como analista de datos, quiero saber si el CSV no incluye alguna columna obligatoria antes de procesar los datos, para evitar validaciones incompletas.

#### Criterios de aceptación

3.1. CUANDO la cabecera del CSV no contiene al menos una columna marcada como `obligatoria: true` en el esquema, EL SISTEMA DEBERÁ generar un hallazgo de tipo `columna_faltante` por cada columna obligatoria ausente, con `fila = 1`, `columna` igual al nombre exacto de la columna ausente y `valor` igual a cadena vacía.

3.2. CUANDO se genera al menos un hallazgo de tipo `columna_faltante`, EL SISTEMA DEBERÁ omitir la validación de filas (reglas 2, 3 y 4) y terminar con código de salida 1.

3.3. CUANDO la cabecera contiene todas las columnas obligatorias, EL SISTEMA DEBERÁ continuar con la validación de filas.

3.4. CUANDO la cabecera contiene columnas adicionales no definidas en el esquema, EL SISTEMA DEBERÁ ignorarlas sin generar hallazgos.

3.5. CUANDO se compara el nombre de una columna de la cabecera con el nombre definido en el esquema, EL SISTEMA DEBERÁ tratar la comparación como sensible a mayúsculas y minúsculas (p. ej. `Fecha` y `fecha` son columnas distintas).

---

### Requisito 4 – Regla 2: tipos por columna

**Historia de usuario:** Como analista de datos, quiero detectar valores con tipo incorrecto en cada columna, para corregir los datos en origen antes de usarlos en analítica.

#### Criterios de aceptación

4.1. CUANDO el valor de una celda no puede convertirse al tipo definido en el esquema para esa columna, EL SISTEMA DEBERÁ generar un hallazgo de tipo `tipo_invalido` indicando fila, columna, tipo esperado y valor encontrado.

4.2. CUANDO el tipo de la columna es `entero`, EL SISTEMA DEBERÁ aceptar únicamente cadenas que representen un número entero sin decimales y sin espacios adicionales (p. ej. `"10"`, `"-3"`); cadenas como `"10.0"`, `"diez"` o `" 10"` deben generar hallazgo `tipo_invalido`.

4.3. CUANDO el tipo de la columna es `decimal`, EL SISTEMA DEBERÁ aceptar cadenas que representen números con o sin parte decimal usando punto como separador y sin espacios adicionales (p. ej. `"15000.50"`, `"8200"`, `"-3.5"`); cadenas con coma decimal o espacios deben generar hallazgo `tipo_invalido`.

4.4. CUANDO el tipo de la columna es `fecha`, EL SISTEMA DEBERÁ aceptar únicamente cadenas que coincidan exactamente con el formato definido en el esquema; `datetime.strptime` con el formato del esquema deberá completarse sin error y sin caracteres sobrantes.

4.5. CUANDO el tipo de la columna es `texto`, EL SISTEMA DEBERÁ aceptar cualquier cadena sin generar hallazgo de tipo.

4.6. CUANDO una columna no es obligatoria y su valor en la fila está vacío, EL SISTEMA DEBERÁ omitir la validación de tipo para esa celda sin generar hallazgo de tipo. CUANDO una columna es obligatoria y su valor está vacío, la regla de vacío (Requisito 5) ya genera un hallazgo y EL SISTEMA DEBERÁ también omitir la validación de tipo para esa celda para evitar hallazgos duplicados.

---

### Requisito 5 – Regla 3: vacíos en columnas obligatorias

**Historia de usuario:** Como analista de datos, quiero detectar celdas vacías en columnas obligatorias, para garantizar que no faltan valores críticos antes de cargar los datos.

#### Criterios de aceptación

5.1. CUANDO el valor de una celda en una columna marcada como `obligatoria: true` está vacío (cadena vacía o cadena compuesta únicamente por espacios), EL SISTEMA DEBERÁ generar exactamente un hallazgo de tipo `vacio_obligatorio` indicando fila y columna; no se generará adicionalmente un hallazgo de tipo `tipo_invalido` para esa misma celda.

5.2. CUANDO el valor de una celda en una columna no obligatoria está vacío, EL SISTEMA DEBERÁ omitir esa celda sin generar hallazgo de tipo `vacio_obligatorio`.

---

### Requisito 6 – Regla 4: duplicados por clave única

**Historia de usuario:** Como analista de datos, quiero detectar filas con clave duplicada, para evitar conteos incorrectos y errores de integridad referencial en el análisis.

#### Criterios de aceptación

6.1. CUANDO una combinación de valores en las columnas definidas como `clave_unica` en el esquema ya ha aparecido en una fila anterior, EL SISTEMA DEBERÁ generar un hallazgo de tipo `duplicado` en la fila de la segunda aparición y en cada aparición posterior; la primera aparición no genera hallazgo.

6.2. CUANDO se genera un hallazgo de tipo `duplicado`, EL SISTEMA DEBERÁ incluir en el campo `mensaje` el número de fila de la primera aparición de esa clave, y en el campo `columna` el nombre de la primera columna de `clave_unica`.

6.3. CUANDO la clave única está compuesta por más de una columna, EL SISTEMA DEBERÁ evaluar la combinación de todas esas columnas como unidad para determinar duplicidad, y en el campo `valor` del hallazgo registrar los valores concatenados con `|` como separador.

6.4. CUANDO alguno de los valores que forman la clave única en una fila está vacío, EL SISTEMA DEBERÁ tratar esa fila como si no tuviese clave válida y omitir la comprobación de duplicados para ella, sin generar hallazgo de tipo `duplicado`.

---

### Requisito 7 – Reporte en consola

**Historia de usuario:** Como analista de datos, quiero leer un resumen claro en la terminal después de ejecutar el validador, para decidir rápidamente si el CSV es apto para usar.

#### Criterios de aceptación

7.1. EL SISTEMA DEBERÁ imprimir siempre en consola el número total de filas de datos leídas (sin contar la cabecera) y el recuento de hallazgos agrupado por tipo de regla (`columna_faltante`, `tipo_invalido`, `vacio_obligatorio`, `duplicado`); los tipos con recuento cero no se muestran.

7.2. CUANDO hay al menos un hallazgo, EL SISTEMA DEBERÁ imprimir una sección de detalle con una línea por hallazgo, ordenada ascendentemente por número de fila, mostrando los campos `fila`, `columna`, `regla`, `valor` y `mensaje` en ese orden.

7.3. CUANDO no hay hallazgos, EL SISTEMA DEBERÁ imprimir el mensaje `Sin hallazgos` y terminar con código de salida 0.

7.4. CUANDO hay al menos un hallazgo, EL SISTEMA DEBERÁ terminar con código de salida 1.

---

### Requisito 8 – Reporte JSON opcional

**Historia de usuario:** Como analista de datos, quiero poder generar un reporte en JSON, para integrarlo con otros procesos automatizados de calidad de datos.

#### Criterios de aceptación

8.1. CUANDO el argumento `--salida-json <ruta>` está presente en la llamada a la CLI, EL SISTEMA DEBERÁ escribir en la ruta indicada un archivo JSON con la siguiente estructura exacta (si el archivo ya existe, sobreescribirlo):

```json
{
  "archivo": "<ruta del CSV>",
  "esquema": "<ruta del esquema>",
  "total_filas": 3,
  "total_hallazgos": 5,
  "hallazgos": [
    {
      "fila": 3,
      "columna": "fecha",
      "regla": "tipo_invalido",
      "valor": "2026/09/02",
      "mensaje": "..."
    }
  ]
}
```

8.2. CUANDO el argumento `--salida-json` no está presente, EL SISTEMA DEBERÁ omitir la generación del archivo JSON sin afectar el reporte en consola ni el código de salida.

8.3. CUANDO el directorio destino del archivo JSON no existe, EL SISTEMA DEBERÁ emitir en consola un mensaje de error descriptivo y terminar con código de salida 2.

---

### Requisito 9 – Interfaz de línea de comandos

**Historia de usuario:** Como analista de datos, quiero invocar el validador con un comando sencillo desde la terminal, para integrarlo en scripts y flujos de trabajo existentes.

#### Criterios de aceptación

9.1. EL SISTEMA DEBERÁ aceptar la invocación `python -m validador <ruta_csv> --esquema <ruta_esquema>`, donde `<ruta_csv>` es un argumento posicional obligatorio y `--esquema` es un argumento nombrado obligatorio.

9.2. CUANDO el argumento posicional `<ruta_csv>` o el argumento `--esquema` no se proporciona en la llamada, EL SISTEMA DEBERÁ mostrar el mensaje de uso en `stderr` y terminar con código de salida 2.

9.3. CUANDO se invoca con `--ayuda` o `-h`, EL SISTEMA DEBERÁ imprimir en consola la descripción de todos los argumentos disponibles (`ruta_csv`, `--esquema`, `--salida-json`, `--ayuda`) y terminar con código de salida 0.

---

### Requisito 10 – Rendimiento

**Historia de usuario:** Como analista de datos, quiero que el validador procese archivos grandes en un tiempo razonable, para no bloquear mis flujos de trabajo al validar exportaciones voluminosas.

#### Criterios de aceptación

10.1. CUANDO el CSV contiene hasta 100 000 filas, EL SISTEMA DEBERÁ completar la validación en menos de 10 segundos en un equipo portátil de uso corriente.

---

### Requisito 11 – Prueba de aceptación extremo a extremo

**Historia de usuario:** Como analista de datos, quiero verificar el comportamiento del validador con los archivos de ejemplo del proyecto, para confirmar que detecta exactamente los problemas esperados.

#### Criterios de aceptación

11.1. CUANDO se valida `datos/ventas_invalido.csv` con `datos/esquema_ventas.json`, EL SISTEMA DEBERÁ producir exactamente 5 hallazgos:
- Fila 3, columna `fecha`: `tipo_invalido` — valor `"2026/09/02"` no coincide con el formato `%Y-%m-%d`.
- Fila 3, columna `cantidad`: `tipo_invalido` — valor `"diez"` no es un entero.
- Fila 4, columna `id_venta`: `duplicado` — valor `"2"` ya apareció en la fila 2.
- Fila 4, columna `cliente`: `vacio_obligatorio` — celda vacía en columna obligatoria.
- Fila 5, columna `valor_unitario`: `vacio_obligatorio` — celda vacía en columna obligatoria.

11.2. CUANDO se valida `datos/ventas_valido.csv` con `datos/esquema_ventas.json`, EL SISTEMA DEBERÁ producir 0 hallazgos y terminar con código de salida 0 (los valores vacíos en la columna `observacion` no son hallazgos porque esa columna no es obligatoria).
