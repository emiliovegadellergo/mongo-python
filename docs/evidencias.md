# Evidencias de pruebas

Generado: 2026-10-27 18:57 por `pruebas/generar_evidencias.py` sobre la base `inventario_pruebas` (se borra al iniciar y al terminar).

**Resultado: 14 de 14 casos se comportaron como se esperaba.**

Los casos se numeran en orden de ejecución: los fallos controlados se ejecutan antes de los borrados porque necesitan que el usuario y el artículo existan.

## Casos de éxito (CRUD)

| # | Operación | Datos de entrada | Esperado | Resultado obtenido | ¿Como se esperaba? |
|---|---|---|---|---|---|
| 1 | Crear usuario | `email='  Ana.Perez@Ejemplo.com ', nombre='Ana', apellido='Pérez'` | Usuario guardado con email normalizado | Usuario creado con email normalizado 'ana.perez@ejemplo.com' | ✅ Sí |
| 2 | Buscar usuario por email | `email='ana.perez@ejemplo.com'` | Devuelve el usuario creado | Encontrado: Ana Pérez <ana.perez@ejemplo.com> | ✅ Sí |
| 3 | Actualizar usuario | `email='ana.perez@ejemplo.com', nombre='Ana María', apellido=None` | Cambia el nombre y conserva el apellido | Guardado: Ana María Pérez (apellido conservado) | ✅ Sí |
| 4 | Crear artículo | `nombre='Laptop', descripcion='14 pulgadas', marca='Dell', usuario='ana.perez@ejemplo.com'` | Artículo guardado con usuario y fecha de modificación | Artículo creado con ID 6ae14891f1424bd03f489ba6, modificó ana.perez@ejemplo.com | ✅ Sí |
| 5 | Buscar artículo por ID | `id='6ae14891f1424bd03f489ba6'` | Devuelve el artículo creado | Encontrado: Laptop / Dell | ✅ Sí |
| 6 | Actualizar artículo | `id='6ae14891f1424bd03f489ba6', usuario='ana.perez@ejemplo.com', nombre=None, marca='Lenovo'` | Cambia la marca, conserva el nombre y renueva fecha_modificado | Guardado: nombre 'Laptop' conservado, marca 'Lenovo', fecha_modificado actualizada | ✅ Sí |
| 13 | Eliminar artículo | `id='6ae14891f1424bd03f489ba6'` | El artículo deja de existir | Eliminado; una búsqueda posterior ya no lo encuentra | ✅ Sí |
| 14 | Eliminar usuario | `email='ana.perez@ejemplo.com'` | El usuario deja de existir al no tener artículos | Eliminado (ya sin artículos); una búsqueda posterior ya no lo encuentra | ✅ Sí |

## Casos de fallo controlado

| # | Operación | Datos de entrada | Esperado | Resultado obtenido | ¿Como se esperaba? |
|---|---|---|---|---|---|
| 7 | Crear artículo con usuario inexistente | `nombre='Mouse', usuario='nadie@ejemplo.com'` | Rechazo con UsuarioNoEncontradoError | UsuarioNoEncontradoError: No existe un usuario con el email nadie@ejemplo.com; registre primero al usuario para poder atribuirle la modificación. | ✅ Sí |
| 8 | Crear artículo con nombre vacío | `nombre='', usuario='ana.perez@ejemplo.com'` | Rechazo con ValidacionError | ValidacionError: El nombre del artículo es obligatorio y no puede ser solo espacios. | ✅ Sí |
| 9 | Crear artículo con nombre de solo espacios | `nombre='    ', usuario='ana.perez@ejemplo.com'` | Rechazo con ValidacionError | ValidacionError: El nombre del artículo es obligatorio y no puede ser solo espacios. | ✅ Sí |
| 10 | Crear usuario con email duplicado | `email='ANA.PEREZ@ejemplo.com' (ya existe normalizado)` | Rechazo con EmailDuplicadoError | EmailDuplicadoError: Ya existe un usuario con el email ana.perez@ejemplo.com. | ✅ Sí |
| 11 | Eliminar usuario con artículos asociados (RESTRICT) | `email='ana.perez@ejemplo.com' (1 artículo lo referencia)` | Rechazo con IntegridadReferencialError | IntegridadReferencialError: No se puede eliminar a ana.perez@ejemplo.com: es el último modificador de 1 artículo(s). Reasigne o elimine esos artículos primero. | ✅ Sí |
| 12 | Buscar artículo con ID mal formado | `id='12345-no-es-id'` | Rechazo con ValidacionError | ValidacionError: '12345-no-es-id' no es un ID válido: debe tener 24 caracteres hexadecimales. | ✅ Sí |
