"""Lectura de datos desde teclado y utilidades de presentación."""

from datetime import datetime
from typing import Callable, Optional

from repositorios.errores import ErrorPersistencia
from servicios.excepciones import InventarioError


def leer_texto(mensaje: str) -> str:
    """Lee una línea tal cual la escribe el usuario."""
    return input(mensaje)


def leer_texto_obligatorio(mensaje: str) -> str:
    """Repite la pregunta hasta recibir un texto no vacío."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  Este dato es obligatorio.")


def leer_opcional(mensaje: str, actual: str) -> Optional[str]:
    """Muestra el valor actual; Enter vacío devuelve ``None`` (conservar)."""
    valor = input(f"{mensaje} [{actual}]: ")
    return valor if valor.strip() else None


def leer_opcion(mensaje: str, minimo: int, maximo: int) -> int:
    """Lee un entero dentro de ``[minimo, maximo]``, repitiendo si no lo es."""
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit() and minimo <= int(valor) <= maximo:
            return int(valor)
        print(f"  Opción inválida: escriba un número entre {minimo} y {maximo}.")


def confirmar(mensaje: str) -> bool:
    """Pregunta s/n hasta recibir una respuesta válida."""
    while True:
        valor = input(f"{mensaje} (s/n): ").strip().lower()
        if valor in ("s", "n"):
            return valor == "s"
        print("  Responda 's' o 'n'.")


def formatear_fecha(fecha: datetime) -> str:
    """Muestra una fecha UTC como YYYY-MM-DD en la zona horaria local."""
    return fecha.astimezone().strftime("%Y-%m-%d")


def titulo(texto: str) -> None:
    """Imprime un encabezado de sección."""
    print(f"\n=== {texto} ===")


def ejecutar_accion(accion: Callable[[], None]) -> None:
    """Ejecuta una acción del menú traduciendo errores a mensajes.

    Las excepciones de negocio y de base de datos nunca cierran el programa.
    """
    try:
        accion()
    except InventarioError as error:
        print(f"  ✗ {error}")
    except ErrorPersistencia as error:
        print(f"  ✗ Error de base de datos, intente de nuevo: {error}")
