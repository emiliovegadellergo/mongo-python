"""Submenú de usuarios."""

from typing import List

from modelos.usuario import Usuario
from servicios.usuario_servicio import UsuarioServicio
from ui.entradas import (confirmar, ejecutar_accion, formatear_fecha,
                         leer_opcion, leer_opcional, leer_texto,
                         leer_texto_obligatorio, titulo)


def _mostrar_usuario(usuario: Usuario) -> None:
    """Imprime el detalle de un usuario."""
    print(f"  Email:    {usuario.email}")
    print(f"  Nombre:   {usuario.nombre}")
    print(f"  Apellido: {usuario.apellido}")
    print(f"  Creado:   {formatear_fecha(usuario.fecha_creado)}")


def _mostrar_tabla(usuarios: List[Usuario]) -> None:
    """Imprime la lista de usuarios en columnas."""
    if not usuarios:
        print("  No hay usuarios registrados.")
        return
    print(f"  {'EMAIL':<30} {'NOMBRE':<20} {'APELLIDO':<20} CREADO")
    for u in usuarios:
        print(f"  {u.email:<30} {u.nombre:<20} {u.apellido:<20} "
              f"{formatear_fecha(u.fecha_creado)}")
    print(f"  Total: {len(usuarios)}")


class MenuUsuarios:
    """Interacción por consola para el CRUD de usuarios."""

    def __init__(self, servicio: UsuarioServicio) -> None:
        """Recibe el servicio de usuarios."""
        self._servicio = servicio

    def ejecutar(self) -> None:
        """Muestra el submenú hasta que el usuario elija Volver."""
        acciones = {1: self._crear, 2: self._listar, 3: self._buscar,
                    4: self._actualizar, 5: self._eliminar}
        while True:
            titulo("USUARIOS")
            print("  1) Crear\n  2) Listar todos\n  3) Buscar por email\n"
                  "  4) Actualizar\n  5) Eliminar\n  0) Volver")
            opcion = leer_opcion("Opción: ", 0, 5)
            if opcion == 0:
                return
            ejecutar_accion(acciones[opcion])

    def _crear(self) -> None:
        """Pide los datos y registra un usuario."""
        titulo("Crear usuario")
        email = leer_texto_obligatorio("Email: ")
        nombre = leer_texto("Nombre: ")
        apellido = leer_texto("Apellido: ")
        usuario = self._servicio.crear(email, nombre, apellido)
        print(f"  ✓ Usuario {usuario.email} creado.")

    def _listar(self) -> None:
        """Muestra todos los usuarios."""
        titulo("Usuarios registrados")
        _mostrar_tabla(self._servicio.listar())

    def _buscar(self) -> None:
        """Busca y muestra un usuario por email."""
        titulo("Buscar usuario")
        _mostrar_usuario(self._servicio.obtener(
            leer_texto_obligatorio("Email: ")))

    def _actualizar(self) -> None:
        """Modifica nombre y apellido; Enter conserva el valor actual."""
        titulo("Actualizar usuario")
        usuario = self._servicio.obtener(leer_texto_obligatorio("Email: "))
        print("  (El email no se puede modificar. Enter conserva el valor.)")
        nombre = leer_opcional("Nombre", usuario.nombre)
        apellido = leer_opcional("Apellido", usuario.apellido)
        self._servicio.actualizar(usuario.email, nombre, apellido)
        print(f"  ✓ Usuario {usuario.email} actualizado.")

    def _eliminar(self) -> None:
        """Elimina un usuario tras confirmar."""
        titulo("Eliminar usuario")
        usuario = self._servicio.obtener(leer_texto_obligatorio("Email: "))
        _mostrar_usuario(usuario)
        if not confirmar("¿Eliminar este usuario?"):
            print("  Operación cancelada.")
            return
        self._servicio.eliminar(usuario.email)
        print(f"  ✓ Usuario {usuario.email} eliminado.")
