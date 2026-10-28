"""Punto de entrada: arma las capas y captura los errores globales."""

import sys

from db.conexion import ErrorConexion, cerrar, conectar
from repositorios.articulo_repositorio import ArticuloRepositorio
from repositorios.errores import ErrorPersistencia
from repositorios.usuario_repositorio import UsuarioRepositorio
from servicios.articulo_servicio import ArticuloServicio
from servicios.usuario_servicio import UsuarioServicio
from ui.menu_articulos import MenuArticulos
from ui.menu_principal import MenuPrincipal
from ui.menu_usuarios import MenuUsuarios


def construir_aplicacion() -> MenuPrincipal:
    """Conecta a MongoDB y crea repositorios, servicios y menús.

    Raises:
        ErrorConexion: si MongoDB no está disponible.
    """
    bd = conectar()
    usuarios_repo = UsuarioRepositorio(bd)
    articulos_repo = ArticuloRepositorio(bd)
    return MenuPrincipal(
        MenuUsuarios(UsuarioServicio(usuarios_repo, articulos_repo)),
        MenuArticulos(ArticuloServicio(articulos_repo, usuarios_repo)),
    )


def main() -> int:
    """Ejecuta la aplicación y devuelve el código de salida."""
    try:
        construir_aplicacion().ejecutar()
        return 0
    except ErrorConexion as error:
        print(f"\n✗ {error}\n  Verifique que el servicio de MongoDB esté "
              "en ejecución (brew services start mongodb-community).")
        return 1
    except ErrorPersistencia as error:
        print(f"\n✗ Se perdió la conexión con la base de datos: {error}")
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\n\nPrograma interrumpido por el usuario. Hasta luego.")
        return 0
    finally:
        cerrar()


if __name__ == "__main__":
    sys.exit(main())
