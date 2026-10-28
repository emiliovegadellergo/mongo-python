"""Genera docs/evidencias.md ejecutando casos de prueba sobre la capa de servicios.

Usa una base separada (``inventario_pruebas``) que se borra al iniciar y al
terminar, de modo que nunca toca los datos reales.

Uso (desde la raíz del proyecto, con el venv activo):
    python pruebas/generar_evidencias.py
"""

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Type

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from db.conexion import (ErrorConexion, cerrar, conectar,  # noqa: E402
                         crear_indices, obtener_cliente)
from repositorios.articulo_repositorio import ArticuloRepositorio  # noqa: E402
from repositorios.usuario_repositorio import UsuarioRepositorio  # noqa: E402
from servicios.articulo_servicio import ArticuloServicio  # noqa: E402
from servicios.excepciones import (ArticuloNoEncontradoError,  # noqa: E402
                                   EmailDuplicadoError,
                                   IntegridadReferencialError,
                                   InventarioError,
                                   UsuarioNoEncontradoError, ValidacionError)
from servicios.usuario_servicio import UsuarioServicio  # noqa: E402

BD_PRUEBAS = "inventario_pruebas"
ARCHIVO_SALIDA = RAIZ / "docs" / "evidencias.md"


@dataclass
class ResultadoCaso:
    """Resultado de un caso de prueba listo para escribirse en el informe."""

    numero: int
    tipo: str
    operacion: str
    entrada: str
    esperado: str
    obtenido: str
    paso: bool


class Evidencias:
    """Ejecuta los casos y acumula sus resultados."""

    def __init__(self) -> None:
        """Inicia la lista de resultados vacía."""
        self.resultados: List[ResultadoCaso] = []

    def _registrar(self, tipo: str, operacion: str, entrada: str,
                   esperado: str, obtenido: str, paso: bool) -> None:
        """Guarda un resultado y lo muestra en consola."""
        numero = len(self.resultados) + 1
        self.resultados.append(ResultadoCaso(numero, tipo, operacion, entrada,
                                             esperado, obtenido, paso))
        marca = "PASÓ" if paso else "FALLÓ"
        print(f"  [{marca}] {numero:02d}. {operacion}")

    def exito(self, operacion: str, entrada: str, esperado: str,
              accion: Callable[[], Any],
              verificar: Callable[[Any], str]) -> Any:
        """Ejecuta un caso que debe terminar sin errores.

        ``verificar`` recibe lo que devolvió la acción, comprueba el estado
        con ``assert`` y devuelve una descripción del resultado obtenido.
        """
        try:
            valor = accion()
            obtenido = verificar(valor)
            paso = True
        except (InventarioError, AssertionError) as error:
            valor = None
            obtenido = f"{type(error).__name__}: {error}"
            paso = False
        self._registrar("Éxito", operacion, entrada, esperado, obtenido, paso)
        return valor

    def fallo(self, operacion: str, entrada: str,
              excepcion: Type[InventarioError],
              accion: Callable[[], Any]) -> None:
        """Ejecuta un caso que debe ser rechazado con ``excepcion``."""
        esperado = f"Rechazo con {excepcion.__name__}"
        try:
            accion()
            obtenido, paso = "La operación se aceptó (no debía)", False
        except InventarioError as error:
            obtenido = f"{type(error).__name__}: {error}"
            paso = isinstance(error, excepcion)
        self._registrar("Fallo controlado", operacion, entrada, esperado,
                        obtenido, paso)


def ejecutar_casos(usuarios: UsuarioServicio,
                   articulos: ArticuloServicio) -> Evidencias:
    """Corre los casos en un orden que deja preparados los datos necesarios."""
    ev = Evidencias()
    print("Ejecutando casos de prueba...")

    def verificar_creado(u: Any) -> str:
        assert u.email == "ana.perez@ejemplo.com"
        return f"Usuario creado con email normalizado '{u.email}'"

    ev.exito("Crear usuario",
             "email='  Ana.Perez@Ejemplo.com ', nombre='Ana', apellido='Pérez'",
             "Usuario guardado con email normalizado",
             lambda: usuarios.crear("  Ana.Perez@Ejemplo.com ", "Ana", "Pérez"),
             verificar_creado)

    def verificar_leido(u: Any) -> str:
        assert (u.nombre, u.apellido) == ("Ana", "Pérez")
        return f"Encontrado: {u.nombre} {u.apellido} <{u.email}>"

    ev.exito("Buscar usuario por email", "email='ana.perez@ejemplo.com'",
             "Devuelve el usuario creado",
             lambda: usuarios.obtener("ana.perez@ejemplo.com"),
             verificar_leido)

    def verificar_actualizado(u: Any) -> str:
        guardado = usuarios.obtener(u.email)
        assert (guardado.nombre, guardado.apellido) == ("Ana María", "Pérez")
        return (f"Guardado: {guardado.nombre} {guardado.apellido} "
                "(apellido conservado)")

    ev.exito("Actualizar usuario",
             "email='ana.perez@ejemplo.com', nombre='Ana María', apellido=None",
             "Cambia el nombre y conserva el apellido",
             lambda: usuarios.actualizar("ana.perez@ejemplo.com", "Ana María"),
             verificar_actualizado)

    def verificar_articulo(a: Any) -> str:
        assert a.id and a.usuario_modifico == "ana.perez@ejemplo.com"
        return f"Artículo creado con ID {a.id}, modificó {a.usuario_modifico}"

    articulo = ev.exito(
        "Crear artículo",
        "nombre='Laptop', descripcion='14 pulgadas', marca='Dell', "
        "usuario='ana.perez@ejemplo.com'",
        "Artículo guardado con usuario y fecha de modificación",
        lambda: articulos.crear("Laptop", "14 pulgadas", "Dell",
                                "ana.perez@ejemplo.com"),
        verificar_articulo)
    id_articulo = articulo.id if articulo else "000000000000000000000000"

    def verificar_articulo_leido(a: Any) -> str:
        assert a.nombre == "Laptop" and a.marca == "Dell"
        return f"Encontrado: {a.nombre} / {a.marca}"

    ev.exito("Buscar artículo por ID", f"id='{id_articulo}'",
             "Devuelve el artículo creado",
             lambda: articulos.obtener(id_articulo), verificar_articulo_leido)

    # Fecha tal como quedó guardada (Mongo la almacena con precisión de ms).
    fecha_antes = (articulos.obtener(id_articulo).fecha_modificado
                   if articulo else None)

    def verificar_articulo_actualizado(_: Any) -> str:
        guardado = articulos.obtener(id_articulo)
        assert guardado.nombre == "Laptop" and guardado.marca == "Lenovo"
        assert fecha_antes is not None and guardado.fecha_modificado > fecha_antes
        return (f"Guardado: nombre '{guardado.nombre}' conservado, marca "
                f"'{guardado.marca}', fecha_modificado actualizada")

    ev.exito("Actualizar artículo",
             f"id='{id_articulo}', usuario='ana.perez@ejemplo.com', "
             "nombre=None, marca='Lenovo'",
             "Cambia la marca, conserva el nombre y renueva fecha_modificado",
             lambda: articulos.actualizar(id_articulo, "ana.perez@ejemplo.com",
                                          marca="Lenovo"),
             verificar_articulo_actualizado)

    # Fallos controlados: requieren que el usuario y el artículo existan.
    ev.fallo("Crear artículo con usuario inexistente",
             "nombre='Mouse', usuario='nadie@ejemplo.com'",
             UsuarioNoEncontradoError,
             lambda: articulos.crear("Mouse", "", "Logitech",
                                     "nadie@ejemplo.com"))
    ev.fallo("Crear artículo con nombre vacío",
             "nombre='', usuario='ana.perez@ejemplo.com'", ValidacionError,
             lambda: articulos.crear("", "", "", "ana.perez@ejemplo.com"))
    ev.fallo("Crear artículo con nombre de solo espacios",
             "nombre='    ', usuario='ana.perez@ejemplo.com'", ValidacionError,
             lambda: articulos.crear("    ", "", "", "ana.perez@ejemplo.com"))
    ev.fallo("Crear usuario con email duplicado",
             "email='ANA.PEREZ@ejemplo.com' (ya existe normalizado)",
             EmailDuplicadoError,
             lambda: usuarios.crear("ANA.PEREZ@ejemplo.com", "Otra", "Ana"))
    ev.fallo("Eliminar usuario con artículos asociados (RESTRICT)",
             "email='ana.perez@ejemplo.com' (1 artículo lo referencia)",
             IntegridadReferencialError,
             lambda: usuarios.eliminar("ana.perez@ejemplo.com"))
    ev.fallo("Buscar artículo con ID mal formado", "id='12345-no-es-id'",
             ValidacionError, lambda: articulos.obtener("12345-no-es-id"))

    def verificar_articulo_eliminado(_: Any) -> str:
        try:
            articulos.obtener(id_articulo)
        except ArticuloNoEncontradoError:
            return "Eliminado; una búsqueda posterior ya no lo encuentra"
        raise AssertionError("El artículo sigue existiendo")

    ev.exito("Eliminar artículo", f"id='{id_articulo}'",
             "El artículo deja de existir",
             lambda: articulos.eliminar(id_articulo),
             verificar_articulo_eliminado)

    def verificar_usuario_eliminado(_: Any) -> str:
        try:
            usuarios.obtener("ana.perez@ejemplo.com")
        except UsuarioNoEncontradoError:
            return "Eliminado (ya sin artículos); búsqueda posterior no lo encuentra"
        raise AssertionError("El usuario sigue existiendo")

    ev.exito("Eliminar usuario", "email='ana.perez@ejemplo.com'",
             "El usuario deja de existir al no tener artículos",
             lambda: usuarios.eliminar("ana.perez@ejemplo.com"),
             verificar_usuario_eliminado)
    return ev


def _celda(texto: str) -> str:
    """Escapa un texto para usarlo dentro de una tabla Markdown."""
    return texto.replace("|", "\\|").replace("\n", " ")


def escribir_informe(ev: Evidencias) -> None:
    """Escribe docs/evidencias.md con una tabla por tipo de caso."""
    aprobados = sum(r.paso for r in ev.resultados)
    lineas = [
        "# Evidencias de pruebas",
        "",
        f"Generado: {datetime.now().astimezone():%Y-%m-%d %H:%M} "
        f"por `pruebas/generar_evidencias.py` sobre la base `{BD_PRUEBAS}` "
        "(se borra al iniciar y al terminar).",
        "",
        f"**Resultado: {aprobados} de {len(ev.resultados)} casos se "
        "comportaron como se esperaba.**",
        "",
        "Los casos se numeran en orden de ejecución: los fallos controlados "
        "se ejecutan antes de los borrados porque necesitan que el usuario y "
        "el artículo existan.",
    ]
    for tipo, encabezado in (("Éxito", "Casos de éxito (CRUD)"),
                             ("Fallo controlado", "Casos de fallo controlado")):
        lineas += ["", f"## {encabezado}", "",
                   "| # | Operación | Datos de entrada | Esperado | "
                   "Resultado obtenido | ¿Como se esperaba? |",
                   "|---|---|---|---|---|---|"]
        for r in ev.resultados:
            if r.tipo == tipo:
                lineas.append(
                    f"| {r.numero} | {_celda(r.operacion)} | "
                    f"`{_celda(r.entrada)}` | {_celda(r.esperado)} | "
                    f"{_celda(r.obtenido)} | {'✅ Sí' if r.paso else '❌ No'} |")
    ARCHIVO_SALIDA.parent.mkdir(exist_ok=True)
    ARCHIVO_SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main() -> int:
    """Prepara la base de pruebas, corre los casos y escribe el informe."""
    try:
        bd = conectar(BD_PRUEBAS)
    except ErrorConexion as error:
        print(f"✗ {error}")
        return 1
    cliente = obtener_cliente()
    try:
        # Se parte de una base vacía; los índices se recrean tras el borrado.
        cliente.drop_database(BD_PRUEBAS)
        crear_indices(bd)
        usuarios_repo = UsuarioRepositorio(bd)
        articulos_repo = ArticuloRepositorio(bd)
        ev = ejecutar_casos(
            UsuarioServicio(usuarios_repo, articulos_repo),
            ArticuloServicio(articulos_repo, usuarios_repo))
        escribir_informe(ev)
    finally:
        cliente.drop_database(BD_PRUEBAS)
        cerrar()
    aprobados = sum(r.paso for r in ev.resultados)
    print(f"\n{aprobados}/{len(ev.resultados)} casos como se esperaba. "
          f"Informe: {ARCHIVO_SALIDA.relative_to(RAIZ)}")
    return 0 if aprobados == len(ev.resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
