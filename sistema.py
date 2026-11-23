# -*- coding: utf-8 -*-
"""
sistema.py
Clase SistemaGestion: administra en listas internas (sin base de datos)
los clientes, servicios y reservas de Software FJ.
"""

from entidades import Cliente  # Clase Cliente
from reservas import Reserva  # Clase Reserva
from excepciones import (  # Excepciones propias
    ClienteDuplicadoError,
    ClienteInvalidoError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
)
from registro_logs import obtener_logger  # Logger del sistema

logger = obtener_logger()  # Obtiene el logger


class SistemaGestion:  # Clase que coordina todo el sistema
    """Gestiona clientes, servicios y reservas usando listas en memoria."""

    def __init__(self):  # Constructor
        self.__clientes = []  # Lista privada de clientes
        self.__servicios = []  # Lista privada de servicios
        self.__reservas = []  # Lista privada de reservas
        logger.info("=== Sistema Software FJ iniciado ===")  # Registra el inicio

    # ---------------- Clientes ----------------

    def registrar_cliente(self, nombre, documento, correo, telefono):  # Crea y guarda un cliente
        """Registra un cliente nuevo validando que no esté duplicado."""
        if self.buscar_cliente(documento, lanzar_error=False):  # Revisa si el documento ya existe
            raise ClienteDuplicadoError(documento)  # Error si está repetido
        cliente = Cliente(nombre, documento, correo, telefono)  # Crea el cliente (valida en el constructor)
        self.__clientes.append(cliente)  # Lo agrega a la lista
        logger.info(f"Cliente registrado: {cliente.describir()}")  # Registra el evento
        return cliente  # Devuelve el cliente creado

    def buscar_cliente(self, documento, lanzar_error=True):  # Busca un cliente por documento
        for cliente in self.__clientes:  # Recorre la lista de clientes
            if cliente.documento == str(documento):  # Compara el documento
                return cliente  # Lo devuelve si lo encuentra
        if lanzar_error:  # Si se pidió lanzar error cuando no exista
            raise ClienteInvalidoError(f"No existe cliente con documento {documento}")  # Error
        return None  # Si no se pidió error, devuelve None

    # ---------------- Servicios ----------------

    def agregar_servicio(self, servicio):  # Guarda un servicio ya creado
        self.__servicios.append(servicio)  # Lo agrega a la lista
        logger.info(f"Servicio agregado: {servicio.describir()}")  # Registra el evento
        return servicio  # Devuelve el servicio

    def buscar_servicio(self, nombre):  # Busca un servicio por nombre
        for servicio in self.__servicios:  # Recorre la lista
            if servicio.nombre.lower() == nombre.lower():  # Compara sin importar mayúsculas
                return servicio  # Lo devuelve si lo encuentra
        raise ServicioNoDisponibleError(nombre)  # Si no existe, no está disponible

    # ---------------- Reservas ----------------

    def crear_reserva(self, documento, nombre_servicio, horas, **parametros):  # Crea una reserva
        """Busca cliente y servicio, y crea la reserva encadenando errores."""
        try:  # Intenta localizar cliente y servicio
            cliente = self.buscar_cliente(documento)  # Puede lanzar ClienteInvalidoError
            servicio = self.buscar_servicio(nombre_servicio)  # Puede lanzar ServicioNoDisponibleError
        except (ClienteInvalidoError, ServicioNoDisponibleError) as error:  # Si alguno falla
            raise ReservaInvalidaError(f"No se pudo crear la reserva: {error.mensaje}") from error  # Encadenamiento
        reserva = Reserva(cliente, servicio, horas, **parametros)  # Crea la reserva (valida internamente)
        self.__reservas.append(reserva)  # La agrega a la lista
        logger.info(f"Reserva creada: {reserva.describir()}")  # Registra el evento
        return reserva  # Devuelve la reserva

    # ---------------- Reportes ----------------

    def resumen(self):  # Devuelve un resumen del estado del sistema
        total = sum(r.costo for r in self.__reservas if r.costo is not None)  # Suma lo facturado
        return {  # Diccionario con los totales
            "clientes": len(self.__clientes),  # Cantidad de clientes
            "servicios": len(self.__servicios),  # Cantidad de servicios
            "reservas": len(self.__reservas),  # Cantidad de reservas
            "facturado": total,  # Dinero facturado
        }

    def listar_reservas(self):  # Devuelve una copia de la lista de reservas
        return list(self.__reservas)  # Copia para proteger la lista interna
