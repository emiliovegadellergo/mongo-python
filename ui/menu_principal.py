"""Menú principal de la aplicación."""

from ui.entradas import leer_opcion, titulo
from ui.menu_articulos import MenuArticulos
from ui.menu_usuarios import MenuUsuarios


class MenuPrincipal:
    """Punto de navegación entre los módulos de usuarios y artículos."""

    def __init__(self, menu_usuarios: MenuUsuarios,
                 menu_articulos: MenuArticulos) -> None:
        """Recibe los submenús ya construidos."""
        self._menu_usuarios = menu_usuarios
        self._menu_articulos = menu_articulos

    def ejecutar(self) -> None:
        """Muestra el menú hasta que el usuario elija Salir."""
        while True:
            titulo("INVENTARIO CON AUDITORÍA")
            print("  1) Usuarios\n  2) Artículos\n  0) Salir")
            opcion = leer_opcion("Opción: ", 0, 2)
            if opcion == 0:
                print("Hasta luego.")
                return
            if opcion == 1:
                self._menu_usuarios.ejecutar()
            else:
                self._menu_articulos.ejecutar()
