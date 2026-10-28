"""Conexión única a MongoDB y creación de índices."""

from typing import Optional

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

import config

# Tiempo máximo (ms) para encontrar un servidor antes de fallar.
TIEMPO_ESPERA_MS = 3000

_cliente: Optional[MongoClient] = None


class ErrorConexion(Exception):
    """Se lanza cuando no es posible conectarse a MongoDB."""


def obtener_cliente(uri: str = config.MONGO_URI) -> MongoClient:
    """Devuelve el cliente de MongoDB, creándolo una sola vez.

    MongoClient ya administra un pool de conexiones internamente, por lo que
    toda la aplicación debe compartir la misma instancia.
    """
    global _cliente
    if _cliente is None:
        _cliente = MongoClient(uri, serverSelectionTimeoutMS=TIEMPO_ESPERA_MS,
                               tz_aware=True)
    return _cliente


def crear_indices(bd: Database) -> None:
    """Crea los índices requeridos; es idempotente si ya existen."""
    bd.usuarios.create_index([("email", ASCENDING)], unique=True,
                             name="ux_usuarios_email")
    bd.articulos.create_index([("usuario_modifico", ASCENDING)],
                              name="ix_articulos_usuario_modifico")


def conectar(nombre_bd: str = config.DB_NAME) -> Database:
    """Verifica la conexión con un ping, crea los índices y devuelve la base.

    Raises:
        ErrorConexion: si el servidor no responde dentro del tiempo límite.
    """
    try:
        cliente = obtener_cliente()
        cliente.admin.command("ping")
        bd = cliente[nombre_bd]
        crear_indices(bd)
        return bd
    except PyMongoError as error:
        raise ErrorConexion(
            f"No se pudo conectar a MongoDB en {config.MONGO_URI}: {error}"
        ) from error


def cerrar() -> None:
    """Cierra el cliente si fue creado."""
    global _cliente
    if _cliente is not None:
        _cliente.close()
        _cliente = None
