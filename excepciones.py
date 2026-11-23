# -*- coding: utf-8 -*-
"""
excepciones.py
Módulo que define la jerarquía de excepciones personalizadas del sistema
Software FJ. Tener excepciones propias permite identificar con precisión
qué tipo de error ocurrió y tratarlo de forma diferente en cada caso.
"""


class SoftwareFJError(Exception):  # Excepción base de la que heredan todas las del sistema
    """Excepción raíz del sistema Software FJ."""

    def __init__(self, mensaje, codigo="FJ-000"):  # Recibe un mensaje y un código de error
        super().__init__(mensaje)  # Inicializa la clase Exception con el mensaje
        self.mensaje = mensaje  # Guarda el mensaje para poder consultarlo después
        self.codigo = codigo  # Guarda el código que identifica el tipo de error

    def __str__(self):  # Define cómo se muestra la excepción como texto
        return f"[{self.codigo}] {self.mensaje}"  # Devuelve el código y el mensaje juntos


class ClienteInvalidoError(SoftwareFJError):  # Error cuando los datos de un cliente no son válidos
    """Se lanza cuando un dato del cliente no cumple las validaciones."""

    def __init__(self, mensaje):  # Solo necesita el mensaje
        super().__init__(mensaje, "FJ-101")  # Asigna el código 101 a los errores de cliente


class ClienteDuplicadoError(SoftwareFJError):  # Error cuando se registra un documento repetido
    """Se lanza al intentar registrar un cliente con un documento ya existente."""

    def __init__(self, documento):  # Recibe el documento repetido
        super().__init__(f"Ya existe un cliente con documento {documento}", "FJ-102")  # Mensaje y código


class ServicioInvalidoError(SoftwareFJError):  # Error en la creación o parámetros de un servicio
    """Se lanza cuando un servicio se crea con parámetros incorrectos."""

    def __init__(self, mensaje):  # Recibe el mensaje descriptivo
        super().__init__(mensaje, "FJ-201")  # Asigna el código 201


class ServicioNoDisponibleError(SoftwareFJError):  # Error cuando el servicio no se puede usar
    """Se lanza cuando se intenta reservar un servicio deshabilitado o inexistente."""

    def __init__(self, nombre_servicio):  # Recibe el nombre del servicio
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible", "FJ-202")  # Mensaje y código


class ReservaInvalidaError(SoftwareFJError):  # Error al crear una reserva con datos incorrectos
    """Se lanza cuando los datos de una reserva no son válidos."""

    def __init__(self, mensaje):  # Recibe el mensaje
        super().__init__(mensaje, "FJ-301")  # Asigna el código 301


class OperacionNoPermitidaError(SoftwareFJError):  # Error por cambio de estado no permitido
    """Se lanza cuando se intenta una operación que el estado actual no permite."""

    def __init__(self, mensaje):  # Recibe el mensaje
        super().__init__(mensaje, "FJ-302")  # Asigna el código 302


class CalculoInconsistenteError(SoftwareFJError):  # Error cuando un cálculo da un valor ilógico
    """Se lanza cuando el cálculo de un costo produce un resultado inconsistente."""

    def __init__(self, mensaje):  # Recibe el mensaje
        super().__init__(mensaje, "FJ-401")  # Asigna el código 401
