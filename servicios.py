# -*- coding: utf-8 -*-
"""
servicios.py
Define la clase abstracta Servicio y sus tres especializaciones:
ReservaSala, AlquilerEquipo y Asesoria. Aquí se aplican herencia,
polimorfismo (métodos sobrescritos) y sobrecarga de métodos.
"""

from abc import abstractmethod  # Para declarar métodos abstractos
from functools import singledispatchmethod  # Permite "sobrecargar" un método según el tipo del argumento

from entidades import Entidad  # Clase abstracta base del sistema
from excepciones import ServicioInvalidoError, CalculoInconsistenteError  # Excepciones propias

IVA = 0.19  # Impuesto al valor agregado en Colombia (19 %)


class Servicio(Entidad):  # Servicio hereda de Entidad y sigue siendo abstracta
    """Servicio genérico ofrecido por Software FJ."""

    def __init__(self, nombre, tarifa_hora):  # Datos comunes a todos los servicios
        super().__init__()  # Asigna id y fecha de creación desde Entidad
        if not isinstance(nombre, str) or not nombre.strip():  # El nombre debe ser texto no vacío
            raise ServicioInvalidoError("El servicio debe tener un nombre")  # Error si falta el nombre
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:  # La tarifa debe ser un número positivo
            raise ServicioInvalidoError(f"Tarifa inválida para '{nombre}': {tarifa_hora}")  # Error si es cero, negativa o texto
        self._nombre = nombre.strip()  # Atributo protegido con el nombre
        self._tarifa_hora = float(tarifa_hora)  # Atributo protegido con la tarifa por hora
        self._disponible = True  # Todo servicio nace disponible

    @property  # Getter del nombre
    def nombre(self):  # Permite leer el nombre
        return self._nombre  # Devuelve el nombre

    @property  # Getter de la disponibilidad
    def disponible(self):  # Indica si el servicio se puede reservar
        return self._disponible  # Devuelve True o False

    def deshabilitar(self):  # Marca el servicio como no disponible
        self._disponible = False  # Cambia el estado a no disponible

    def habilitar(self):  # Vuelve a poner el servicio disponible
        self._disponible = True  # Cambia el estado a disponible

    # ---------------- Métodos abstractos (polimorfismo) ----------------

    @abstractmethod  # Cada servicio calcula su costo de forma distinta
    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, **parametros):  # Firma común
        """Calcula el costo del servicio para una cantidad de horas."""

    @abstractmethod  # Cada servicio valida sus propios parámetros
    def validar_parametros(self, horas, **parametros):  # Firma común
        """Verifica que los parámetros de uso sean válidos."""

    def validar(self):  # Implementa el método abstracto de Entidad
        return self._tarifa_hora > 0 and bool(self._nombre)  # Un servicio es válido si tiene nombre y tarifa

    # ---------------- Método auxiliar común ----------------

    def _aplicar_ajustes(self, subtotal, impuesto, descuento):  # Aplica descuento e impuesto a un subtotal
        """Aplica descuento e impuesto y verifica que el resultado sea coherente."""
        if not 0 <= descuento < 1:  # El descuento va de 0 % a menos de 100 %
            raise CalculoInconsistenteError(f"Descuento fuera de rango: {descuento}")  # Error si es ilógico
        if not 0 <= impuesto <= 0.5:  # El impuesto no puede ser negativo ni exagerado
            raise CalculoInconsistenteError(f"Impuesto fuera de rango: {impuesto}")  # Error si es ilógico
        total = subtotal * (1 - descuento) * (1 + impuesto)  # Primero descuento, luego impuesto
        if total <= 0:  # Un costo final nunca puede ser cero o negativo
            raise CalculoInconsistenteError(f"Costo calculado inconsistente: {total}")  # Error de cálculo
        return round(total, 2)  # Redondea a dos decimales

    # ---------------- Sobrecarga de métodos ----------------
    # Python no permite definir dos métodos con el mismo nombre y distintos
    # parámetros (como Java). Para simular la sobrecarga se usa
    # singledispatchmethod, que elige la versión según el tipo del argumento.

    @singledispatchmethod  # Versión por defecto de cotizar
    def cotizar(self, argumento):  # Se ejecuta si el tipo no coincide con ninguna variante
        raise ServicioInvalidoError(f"Tipo de cotización no soportado: {type(argumento).__name__}")  # Error de tipo

    @cotizar.register  # Variante 1: cotizar(horas) con un número entero
    def _(self, horas: int):  # Recibe solo las horas
        return self.calcular_costo(horas)  # Costo sin impuesto ni descuento

    @cotizar.register  # Variante 2: cotizar((horas, descuento)) con una tupla
    def _(self, datos: tuple):  # Recibe horas y descuento
        horas, descuento = datos  # Separa los dos valores de la tupla
        return self.calcular_costo(horas, impuesto=IVA, descuento=descuento)  # Costo con IVA y descuento

    @cotizar.register  # Variante 3: cotizar({...}) con un diccionario de opciones
    def _(self, opciones: dict):  # Recibe todos los parámetros con nombre
        datos = dict(opciones)  # Copia para no modificar el diccionario original
        horas = datos.pop("horas", None)  # Extrae las horas (obligatorias)
        if horas is None:  # Si no vienen las horas
            raise ServicioInvalidoError("Falta el parámetro 'horas' en la cotización")  # Parámetro faltante
        return self.calcular_costo(horas, **datos)  # Pasa el resto como parámetros opcionales

    def __str__(self):  # Representación en texto
        return self.describir()  # Reutiliza describir, que cada hija sobrescribe


class ReservaSala(Servicio):  # Primer servicio especializado
    """Reserva de salas de reuniones o capacitación."""

    def __init__(self, nombre, tarifa_hora, capacidad):  # Agrega la capacidad de la sala
        super().__init__(nombre, tarifa_hora)  # Inicializa la parte común
        if not isinstance(capacidad, int) or capacidad <= 0:  # La capacidad debe ser entero positivo
            raise ServicioInvalidoError(f"Capacidad inválida para la sala '{nombre}': {capacidad}")  # Error
        self._capacidad = capacidad  # Guarda la capacidad máxima

    def validar_parametros(self, horas, **parametros):  # Sobrescribe la validación
        personas = parametros.get("personas", 1)  # Número de asistentes (1 por defecto)
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 12:  # Una sala se alquila de 1 a 12 horas
            raise ServicioInvalidoError(f"Horas inválidas para sala: {horas}")  # Error si se sale del rango
        if personas > self._capacidad:  # No se puede superar la capacidad
            raise ServicioInvalidoError(f"La sala '{self._nombre}' admite {self._capacidad} personas, se pidieron {personas}")  # Error
        return True  # Parámetros correctos

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, **parametros):  # Sobrescribe el cálculo
        self.validar_parametros(horas, **parametros)  # Primero valida
        subtotal = self._tarifa_hora * horas  # Tarifa por hora multiplicada por las horas
        if horas >= 8:  # Si se reserva la jornada completa
            subtotal *= 0.9  # Se aplica un 10 % de descuento por jornada
        return self._aplicar_ajustes(subtotal, impuesto, descuento)  # Aplica impuestos y descuentos

    def describir(self):  # Sobrescribe la descripción
        return f"Sala '{self._nombre}' - capacidad {self._capacidad} personas - ${self._tarifa_hora:,.0f}/hora"  # Texto


class AlquilerEquipo(Servicio):  # Segundo servicio especializado
    """Alquiler de equipos (portátiles, proyectores, etc.)."""

    DEPOSITO_POR_UNIDAD = 20000  # Depósito fijo por cada equipo alquilado

    def __init__(self, nombre, tarifa_hora, unidades):  # Agrega las unidades en inventario
        super().__init__(nombre, tarifa_hora)  # Inicializa la parte común
        if not isinstance(unidades, int) or unidades < 0:  # Las unidades deben ser un entero no negativo
            raise ServicioInvalidoError(f"Unidades inválidas para '{nombre}': {unidades}")  # Error
        self._unidades = unidades  # Guarda la cantidad disponible
        if unidades == 0:  # Si no hay equipos en inventario
            self.deshabilitar()  # El servicio queda no disponible

    def validar_parametros(self, horas, **parametros):  # Sobrescribe la validación
        cantidad = parametros.get("cantidad", 1)  # Equipos solicitados (1 por defecto)
        if not isinstance(horas, (int, float)) or horas <= 0:  # Las horas deben ser positivas
            raise ServicioInvalidoError(f"Horas inválidas para alquiler: {horas}")  # Error
        if not isinstance(cantidad, int) or cantidad <= 0:  # La cantidad debe ser entero positivo
            raise ServicioInvalidoError(f"Cantidad de equipos inválida: {cantidad}")  # Error
        if cantidad > self._unidades:  # No se pueden alquilar más equipos de los que hay
            raise ServicioInvalidoError(f"Solo hay {self._unidades} unidades de '{self._nombre}', se pidieron {cantidad}")  # Error
        return True  # Parámetros correctos

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, **parametros):  # Sobrescribe el cálculo
        self.validar_parametros(horas, **parametros)  # Primero valida
        cantidad = parametros.get("cantidad", 1)  # Cantidad de equipos
        subtotal = self._tarifa_hora * horas * cantidad  # Tarifa × horas × cantidad
        subtotal += self.DEPOSITO_POR_UNIDAD * cantidad  # Suma el depósito por cada equipo
        return self._aplicar_ajustes(subtotal, impuesto, descuento)  # Aplica impuestos y descuentos

    def describir(self):  # Sobrescribe la descripción
        return f"Equipo '{self._nombre}' - {self._unidades} unidades - ${self._tarifa_hora:,.0f}/hora"  # Texto


class Asesoria(Servicio):  # Tercer servicio especializado
    """Asesoría especializada con un consultor."""

    NIVELES = {"basico": 1.0, "intermedio": 1.3, "experto": 1.7}  # Multiplicador de tarifa según el nivel

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="basico"):  # Agrega especialidad y nivel
        super().__init__(nombre, tarifa_hora)  # Inicializa la parte común
        if nivel not in self.NIVELES:  # El nivel debe ser uno de los definidos
            raise ServicioInvalidoError(f"Nivel '{nivel}' no existe. Use: {', '.join(self.NIVELES)}")  # Error
        if not isinstance(especialidad, str) or not especialidad.strip():  # La especialidad es obligatoria
            raise ServicioInvalidoError("La asesoría debe indicar una especialidad")  # Error
        self._especialidad = especialidad.strip()  # Guarda la especialidad
        self._nivel = nivel  # Guarda el nivel

    def validar_parametros(self, horas, **parametros):  # Sobrescribe la validación
        if not isinstance(horas, (int, float)) or not 0.5 <= horas <= 8:  # Asesorías de 30 min a 8 horas
            raise ServicioInvalidoError(f"Horas inválidas para asesoría: {horas}")  # Error
        return True  # Parámetros correctos

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0, **parametros):  # Sobrescribe el cálculo
        self.validar_parametros(horas, **parametros)  # Primero valida
        subtotal = self._tarifa_hora * self.NIVELES[self._nivel] * horas  # Tarifa × nivel × horas
        return self._aplicar_ajustes(subtotal, impuesto, descuento)  # Aplica impuestos y descuentos

    def describir(self):  # Sobrescribe la descripción
        return f"Asesoría '{self._nombre}' en {self._especialidad} (nivel {self._nivel}) - ${self._tarifa_hora:,.0f}/hora"  # Texto
