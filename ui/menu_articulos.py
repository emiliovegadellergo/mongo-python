"""Submenú de artículos."""

from typing import List

from modelos.articulo import Articulo
from servicios.articulo_servicio import ArticuloServicio
from ui.entradas import (confirmar, ejecutar_accion, formatear_fecha,
                         leer_opcion, leer_opcional, leer_texto,
                         leer_texto_obligatorio, titulo)


def _recortar(texto: str, ancho: int) -> str:
    """Acorta el texto para que quepa en una columna."""
    return texto if len(texto) <= ancho else texto[:ancho - 1] + "…"


def _mostrar_articulo(articulo: Articulo) -> None:
    """Imprime el detalle de un artículo."""
    print(f"  ID:           {articulo.id}")
    print(f"  Nombre:       {articulo.nombre}")
    print(f"  Descripción:  {articulo.descripcion}")
    print(f"  Marca:        {articulo.marca}")
    print(f"  Modificó:     {articulo.usuario_modifico}")
    print(f"  Fecha modif.: {formatear_fecha(articulo.fecha_modificado)}")


def _mostrar_tabla(articulos: List[Articulo]) -> None:
    """Imprime la lista de artículos con su ID para poder copiarlo."""
    if not articulos:
        print("  No hay artículos registrados.")
        return
    print(f"  {'ID':<24} {'NOMBRE':<22} {'MARCA':<14} {'MODIFICÓ':<26} FECHA")
    for a in articulos:
        print(f"  {a.id:<24} {_recortar(a.nombre, 22):<22} "
              f"{_recortar(a.marca, 14):<14} "
              f"{_recortar(a.usuario_modifico, 26):<26} "
              f"{formatear_fecha(a.fecha_modificado)}")
    print(f"  Total: {len(articulos)}")


class MenuArticulos:
    """Interacción por consola para el CRUD de artículos."""

    def __init__(self, servicio: ArticuloServicio) -> None:
        """Recibe el servicio de artículos."""
        self._servicio = servicio

    def ejecutar(self) -> None:
        """Muestra el submenú hasta que el usuario elija Volver."""
        acciones = {1: self._crear, 2: self._listar, 3: self._buscar,
                    4: self._actualizar, 5: self._eliminar}
        while True:
            titulo("ARTÍCULOS")
            print("  1) Crear\n  2) Listar todos\n  3) Buscar por ID\n"
                  "  4) Actualizar\n  5) Eliminar\n  0) Volver")
            opcion = leer_opcion("Opción: ", 0, 5)
            if opcion == 0:
                return
            ejecutar_accion(acciones[opcion])

    def _pedir_responsable(self) -> str:
        """Pide el email del responsable y verifica de inmediato que exista."""
        email = self._servicio.validar_responsable(
            leer_texto_obligatorio("Email del usuario responsable: "))
        print(f"  ✓ Responsable verificado: {email}")
        return email

    def _crear(self) -> None:
        """Pide los datos y registra un artículo."""
        titulo("Crear artículo")
        email = self._pedir_responsable()
        nombre = leer_texto_obligatorio("Nombre: ")
        descripcion = leer_texto("Descripción: ")
        marca = leer_texto("Marca: ")
        articulo = self._servicio.crear(nombre, descripcion, marca, email)
        print(f"  ✓ Artículo creado con ID {articulo.id}")

    def _listar(self) -> None:
        """Muestra todos los artículos."""
        titulo("Artículos registrados")
        _mostrar_tabla(self._servicio.listar())

    def _buscar(self) -> None:
        """Busca y muestra un artículo por ID."""
        titulo("Buscar artículo")
        _mostrar_articulo(self._servicio.obtener(
            leer_texto_obligatorio("ID del artículo: ")))

    def _actualizar(self) -> None:
        """Modifica un artículo; Enter conserva el valor de cada campo."""
        titulo("Actualizar artículo")
        articulo = self._servicio.obtener(
            leer_texto_obligatorio("ID del artículo: "))
        _mostrar_articulo(articulo)
        email = self._pedir_responsable()
        print("  (Enter conserva el valor actual.)")
        nombre = leer_opcional("Nombre", articulo.nombre)
        descripcion = leer_opcional("Descripción", articulo.descripcion)
        marca = leer_opcional("Marca", articulo.marca)
        self._servicio.actualizar(articulo.id, email, nombre, descripcion,
                                  marca)
        print(f"  ✓ Artículo {articulo.id} actualizado por {email}.")

    def _eliminar(self) -> None:
        """Elimina un artículo tras confirmar."""
        titulo("Eliminar artículo")
        articulo = self._servicio.obtener(
            leer_texto_obligatorio("ID del artículo: "))
        _mostrar_articulo(articulo)
        if not confirmar("¿Eliminar este artículo?"):
            print("  Operación cancelada.")
            return
        self._servicio.eliminar(articulo.id)
        print(f"  ✓ Artículo {articulo.id} eliminado.")
