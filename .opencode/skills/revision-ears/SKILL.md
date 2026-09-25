---
name: revision-ears
description: Checklist de revisión contra criterios EARS y estándares de steering del validador-csv. Úsala al revisar cualquier cambio de código.
---
# Checklist de revisión

## A. Trazabilidad (bloqueante)
- [ ] Cada criterio EARS citado tiene al menos una prueba test_req_<n>_<m>_*.
- [ ] La prueba prepara la condición del CUANDO y comprueba el DEBERÁ.
- [ ] No hay funcionalidad que ningún criterio pida (sobre-implementación).

## B. Estándares de tech.md (bloqueante)
- [ ] Solo biblioteca estándar en src/.
- [ ] Type hints y docstring en funciones públicas.
- [ ] Sin print ni sys.exit fuera de cli.py.
- [ ] Sin except genéricos que oculten errores.
- [ ] CSV abiertos con encoding "utf-8-sig".

## C. Estructura de structure.md (bloqueante)
- [ ] Archivos solo en src/validador/ y tests/.
- [ ] Lectura, reglas y presentación en módulos separados.

## D. Calidad (menor)
- [ ] Nombres claros en español sin tildes.
- [ ] Mensajes al usuario con fila y columna cuando aplica.
- [ ] Sin código muerto ni comentarios obsoletos.

## Cómo leer un criterio EARS
"CUANDO el CSV no contiene una columna obligatoria, EL SISTEMA DEBERÁ reportar
un hallazgo con regla columna_faltante por cada columna ausente."
- Condición a preparar: un CSV sin esa columna.
- Resultado a verificar: un hallazgo por columna ausente. Ni más ni menos.