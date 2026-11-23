# -*- coding: utf-8 -*-
"""
reservas.py
Define la clase Reserva, que une un cliente, un servicio, una duración y
un estado. Implementa confirmación, cancelación y procesamiento con manejo
de excepciones (try/except/else/finally y encadenamiento).
"""

from entidades import Entidad, Cliente  # Clase base y clase Cliente
from servicios import Servicio, IVA  # Clase Servicio y el valor del IVA
from excepciones import (  # Excepciones propias usadas en este módulo
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
    SoftwareFJError,
)
from registro_logs import obtener_logger  # Logger del sistema

logger = obtener_logger()  # Obtiene el logger para registrar eventos


class Reserva(Entidad):  # Reserva hereda de Entidad
    """Reserva de un servicio realizada por un cliente."""

    PENDIENTE = "PENDIENTE"  # Estado inicial de toda reserva
    CONFIRMADA = "CONFIRMADA"  # Estado cuando la reserva se confirma
    PROCESADA = "PROCESADA"  # Estado cuando el servicio ya se cobró
    CANCELADA = "CANCELADA"  # Estado cuando la reserva se cancela

    def __init__(self, cliente, servicio, horas, **parametros):  # Datos necesarios para reservar
        super().__init__()  # Asigna id y fecha desde Entidad
        self._cliente = cliente  # Cliente que reserva
        self._servicio = servicio  # Servicio reservado
        self._horas = horas  # Duración en horas
        self._parametros = parametros  # Parámetros extra (personas, cantidad, etc.)
        self._estado = Reserva.PENDIENTE  # Toda reserva empieza pendiente
        self._costo = None  # El costo se calcula al procesar
        self.validar()  # Valida todo antes de dar la reserva por creada

    @property  # Getter del estado
    def estado(self):  # Permite consultar el estado
        return self._estado  # Devuelve el estado actual

    @property  # Getter del costo
    def costo(self):  # Permite consultar el costo final
        return self._costo  # Devuelve el costo (None si no se ha procesado)

    def validar(self):  # Implementa el método abstracto de Entidad
        """Verifica que cliente, servicio y duración sean correctos."""
        if not isinstance(self._cliente, Cliente):  # Debe recibirse un objeto Cliente
            raise ReservaInvalidaError("La reserva necesita un cliente válido")  # Error si no lo es
        if not isinstance(self._servicio, Servicio):  # Debe recibirse un objeto Servicio
            raise ReservaInvalidaError("La reserva necesita un servicio válido")  # Error si no lo es
        if not self._servicio.disponible:  # El servicio debe estar habilitado
            raise ServicioNoDisponibleError(self._servicio.nombre)  # Error si está deshabilitado
        if self._horas is None:  # La duración es obligatoria
            raise ReservaInvalidaError("Falta la duración de la reserva")  # Parámetro faltante
        try:  # Intenta validar los parámetros con las reglas del servicio
            self._servicio.validar_parametros(self._horas, **self._parametros)  # Validación polimórfica
        except SoftwareFJError as error:  # Si el servicio rechaza los parámetros
            raise ReservaInvalidaError(f"Parámetros rechazados por el servicio: {error.mensaje}") from error  # Encadenamiento
        return True  # Todo correcto

    def confirmar(self):  # Pasa la reserva de PENDIENTE a CONFIRMADA
        """Confirma la reserva si está pendiente."""
        if self._estado != Reserva.PENDIENTE:  # Solo se confirman reservas pendientes
            raise OperacionNoPermitidaError(f"No se puede confirmar la reserva #{self.id} en estado {self._estado}")  # Error
        self._estado = Reserva.CONFIRMADA  # Cambia el estado
        logger.info(f"Reserva #{self.id} confirmada")  # Registra el evento

    def cancelar(self):  # Cancela la reserva
        """Cancela la reserva si todavía no fue procesada."""
        if self._estado in (Reserva.PROCESADA, Reserva.CANCELADA):  # No se cancela lo ya cobrado o cancelado
            raise OperacionNoPermitidaError(f"No se puede cancelar la reserva #{self.id} en estado {self._estado}")  # Error
        self._estado = Reserva.CANCELADA  # Cambia el estado
        logger.info(f"Reserva #{self.id} cancelada")  # Registra el evento

    def procesar(self, descuento=0.0):  # Calcula el costo y cierra la reserva
        """Calcula el costo final con IVA. Usa try/except/else/finally."""
        if self._estado != Reserva.CONFIRMADA:  # Solo se procesan reservas confirmadas
            raise OperacionNoPermitidaError(f"La reserva #{self.id} debe estar CONFIRMADA para procesarse (está {self._estado})")  # Error
        try:  # Bloque que puede fallar: el cálculo del costo
            costo = self._servicio.calcular_costo(  # Llamada polimórfica: cada servicio calcula distinto
                self._horas, impuesto=IVA, descuento=descuento, **self._parametros
            )
        except SoftwareFJError as error:  # Si el cálculo falla
            logger.error(f"Fallo al procesar reserva #{self.id}: {error}")  # Registra el error
            raise ReservaInvalidaError(f"No se pudo procesar la reserva #{self.id}") from error  # Encadena la excepción
        else:  # Solo se ejecuta si no hubo error en el try
            self._costo = costo  # Guarda el costo calculado
            self._estado = Reserva.PROCESADA  # Marca la reserva como procesada
            logger.info(f"Reserva #{self.id} procesada por ${costo:,.2f}")  # Registra el éxito
            return costo  # Devuelve el costo
        finally:  # Se ejecuta siempre, haya o no error
            logger.debug(f"Fin del intento de procesamiento de la reserva #{self.id}")  # Deja traza del intento

    def describir(self):  # Implementa el método abstracto de Entidad
        costo = f"${self._costo:,.2f}" if self._costo is not None else "sin calcular"  # Texto del costo
        return (f"Reserva #{self.id} | {self._cliente.nombre} | {self._servicio.nombre} | "
                f"{self._horas} h | {self._estado} | {costo}")  # Descripción completa

    def __str__(self):  # Representación en texto
        return self.describir()  # Reutiliza describir
