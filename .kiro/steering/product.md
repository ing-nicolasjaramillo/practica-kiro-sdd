---
inclusion: always
---
# Producto: validador-csv

## Propósito
Herramienta de línea de comandos que valida archivos CSV contra un esquema JSON
antes de usarlos en procesos de analítica. Detecta problemas de calidad de datos
temprano y produce un reporte legible y otro procesable por máquina.

## Usuario objetivo
Analista de datos que recibe CSV exportados de otros sistemas (ERP, Excel) y
necesita saber, antes de usarlos, si cumplen el contrato esperado.

## Alcance versión 1
Incluye:
- Validar que existan las columnas obligatorias del esquema.
- Validar tipos por columna: texto, entero, decimal, fecha (formato configurable).
- Detectar valores vacíos en columnas obligatorias.
- Detectar duplicados según la clave única del esquema.
- Reporte en consola (resumen + detalle) y reporte opcional en JSON.
- Códigos de salida: 0 sin hallazgos, 1 con hallazgos, 2 error de uso o de archivo.

Fuera de alcance:
- Corregir o transformar datos.
- Interfaz gráfica o web.
- Conexión a bases de datos o nube.
- Formatos distintos de CSV (Excel, Parquet).

## Criterios de éxito
- Un CSV válido termina con código 0 y el mensaje "Sin hallazgos".
- Cada hallazgo indica fila, columna, regla incumplida y valor encontrado.
- Procesa 100.000 filas en menos de 10 segundos en un portátil corriente.

## Glosario
- Esquema: archivo JSON con columnas, tipos y clave única.
- Hallazgo: incumplimiento de una regla en una fila y columna concretas.
- Regla: una verificación (columna faltante, tipo inválido, vacío obligatorio, duplicado).

## Idioma
Documentación, specs, mensajes al usuario y comentarios en español.
Requisitos en formato EARS: "CUANDO <condición>, EL SISTEMA DEBERÁ <comportamiento>".