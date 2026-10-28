"""Configuración de la aplicación.

Los valores por defecto apuntan al servicio local de MongoDB y se pueden
sobrescribir con las variables de entorno ``MONGO_URI`` y ``DB_NAME``.
"""

import os

MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME: str = os.getenv("DB_NAME", "inventario")
