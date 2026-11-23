# -*- coding: utf-8 -*-
"""
entidades.py
Contiene la clase abstracta Entidad (base de todo el sistema) y la clase
Cliente, que encapsula los datos personales y los valida.
"""

import re  # Expresiones regulares para validar el formato del correo
from abc import ABC, abstractmethod  # Herramientas para crear clases abstractas
from datetime import datetime  # Para guardar la fecha de creación de cada entidad

from excepciones import ClienteInvalidoError  # Excepción propia para datos de cliente erróneos


class Entidad(ABC):  # Clase abstracta: no se puede instanciar directamente
    """Representa cualquier entidad general del sistema (cliente, servicio, reserva)."""

    _contador = 0  # Atributo de clase compartido para generar identificadores únicos

    def __init__(self):  # Constructor común a todas las entidades
        Entidad._contador += 1  # Aumenta el contador global cada vez que se crea una entidad
        self._id = Entidad._contador  # Asigna el identificador único (atributo protegido)
        self._fecha_creacion = datetime.now()  # Guarda la fecha y hora de creación

    @property  # Permite leer el id como atributo, pero no modificarlo
    def id(self):  # Getter del identificador
        return self._id  # Devuelve el id

    @abstractmethod  # Obliga a las clases hijas a implementar este método
    def describir(self):  # Cada entidad debe saber describirse a sí misma
        """Devuelve una descripción en texto de la entidad."""

    @abstractmethod  # Obliga a las clases hijas a implementar este método
    def validar(self):  # Cada entidad debe validar sus propios datos
        """Valida los datos de la entidad y lanza una excepción si algo falla."""


class Cliente(Entidad):  # Cliente hereda de Entidad
    """Cliente de Software FJ con datos personales encapsulados."""

    PATRON_CORREO = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")  # Patrón válido de correo electrónico

    def __init__(self, nombre, documento, correo, telefono):  # Recibe los datos personales
        super().__init__()  # Ejecuta el constructor de Entidad (id y fecha)
        self.__nombre = None  # Atributo privado (doble guion bajo = encapsulación)
        self.__documento = None  # Atributo privado del documento
        self.__correo = None  # Atributo privado del correo
        self.__telefono = None  # Atributo privado del teléfono
        self.nombre = nombre  # Usa el setter, que valida el nombre
        self.documento = documento  # Usa el setter, que valida el documento
        self.correo = correo  # Usa el setter, que valida el correo
        self.telefono = telefono  # Usa el setter, que valida el teléfono

    # ---------------- Propiedades con validación (encapsulación) ----------------

    @property  # Getter del nombre
    def nombre(self):  # Permite leer el nombre
        return self.__nombre  # Devuelve el valor privado

    @nombre.setter  # Setter del nombre
    def nombre(self, valor):  # Valida antes de asignar
        if not isinstance(valor, str) or not valor.strip():  # El nombre debe ser texto no vacío
            raise ClienteInvalidoError("El nombre es obligatorio y debe ser texto")  # Error si está vacío
        if not all(parte.isalpha() for parte in valor.split()):  # Solo letras (permite espacios)
            raise ClienteInvalidoError(f"El nombre '{valor}' contiene caracteres no válidos")  # Error si hay números o símbolos
        self.__nombre = valor.strip().title()  # Guarda el nombre limpio y con mayúscula inicial

    @property  # Getter del documento
    def documento(self):  # Permite leer el documento
        return self.__documento  # Devuelve el valor privado

    @documento.setter  # Setter del documento
    def documento(self, valor):  # Valida antes de asignar
        valor = str(valor).strip()  # Convierte a texto y quita espacios
        if not valor.isdigit() or not 6 <= len(valor) <= 10:  # Debe tener solo dígitos, entre 6 y 10
            raise ClienteInvalidoError(f"Documento '{valor}' inválido: debe tener de 6 a 10 dígitos")  # Error si no cumple
        self.__documento = valor  # Guarda el documento validado

    @property  # Getter del correo
    def correo(self):  # Permite leer el correo
        return self.__correo  # Devuelve el valor privado

    @correo.setter  # Setter del correo
    def correo(self, valor):  # Valida antes de asignar
        if not isinstance(valor, str) or not self.PATRON_CORREO.match(valor):  # Compara con el patrón
            raise ClienteInvalidoError(f"Correo '{valor}' con formato inválido")  # Error si no coincide
        self.__correo = valor.lower()  # Guarda el correo en minúsculas

    @property  # Getter del teléfono
    def telefono(self):  # Permite leer el teléfono
        return self.__telefono  # Devuelve el valor privado

    @telefono.setter  # Setter del teléfono
    def telefono(self, valor):  # Valida antes de asignar
        valor = str(valor).strip()  # Convierte a texto y quita espacios
        if not valor.isdigit() or len(valor) != 10:  # Celular colombiano: 10 dígitos
            raise ClienteInvalidoError(f"Teléfono '{valor}' inválido: debe tener 10 dígitos")  # Error si no cumple
        self.__telefono = valor  # Guarda el teléfono validado

    # ---------------- Métodos abstractos implementados ----------------

    def validar(self):  # Implementación obligatoria del método abstracto
        """Revalida todos los datos del cliente (útil antes de reservar)."""
        self.nombre = self.__nombre  # Vuelve a pasar el nombre por su validación
        self.documento = self.__documento  # Vuelve a validar el documento
        self.correo = self.__correo  # Vuelve a validar el correo
        self.telefono = self.__telefono  # Vuelve a validar el teléfono
        return True  # Si no se lanzó ninguna excepción, el cliente es válido

    def describir(self):  # Implementación obligatoria del método abstracto
        """Describe al cliente ocultando parte del documento (protección de datos)."""
        doc_oculto = "*" * (len(self.__documento) - 4) + self.__documento[-4:]  # Muestra solo los 4 últimos dígitos
        return f"Cliente #{self.id}: {self.__nombre} (Doc. {doc_oculto}, {self.__correo})"  # Texto descriptivo

    def __str__(self):  # Representación en texto al usar print()
        return self.describir()  # Reutiliza el método describir
