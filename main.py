# -*- coding: utf-8 -*-
"""
main.py
Punto de entrada del sistema Software FJ. Simula más de 10 operaciones
completas (válidas e inválidas) para demostrar que el programa sigue
funcionando aunque ocurran errores.

Ejecutar con:  python main.py
"""

from sistema import SistemaGestion  # Clase que gestiona todo
from servicios import ReservaSala, AlquilerEquipo, Asesoria  # Servicios especializados
from excepciones import SoftwareFJError  # Excepción base del sistema
from registro_logs import obtener_logger, ARCHIVO_LOG  # Logger y ruta del archivo de logs

logger = obtener_logger()  # Obtiene el logger
resultados = {"exitosas": 0, "fallidas": 0}  # Contador de operaciones


def ejecutar(numero, descripcion, operacion):  # Ejecuta una operación sin detener el programa
    """Ejecuta una operación y captura cualquier error para que el sistema siga activo."""
    print(f"\n[{numero:02d}] {descripcion}")  # Muestra qué operación se va a ejecutar
    try:  # Intenta realizar la operación
        resultado = operacion()  # Ejecuta la función recibida
    except SoftwareFJError as error:  # Errores previstos del sistema
        resultados["fallidas"] += 1  # Cuenta la operación fallida
        print(f"     ✗ Error controlado: {error}")  # Muestra el error
        if error.__cause__:  # Si la excepción fue encadenada
            print(f"       Causa original: {error.__cause__}")  # Muestra la causa
        logger.warning(f"Op {numero} fallida: {error} | causa: {error.__cause__}")  # Registra el error
    except Exception as error:  # Cualquier error inesperado
        resultados["fallidas"] += 1  # Cuenta la operación fallida
        print(f"     ✗ Error inesperado: {type(error).__name__}: {error}")  # Muestra el error
        logger.critical(f"Op {numero} error inesperado: {type(error).__name__}: {error}")  # Registra como crítico
    else:  # Solo si no hubo error
        resultados["exitosas"] += 1  # Cuenta la operación exitosa
        print(f"     ✓ {resultado}")  # Muestra el resultado
        logger.info(f"Op {numero} exitosa: {resultado}")  # Registra el éxito
    finally:  # Siempre se ejecuta
        logger.debug(f"Op {numero} finalizada")  # Deja traza de que terminó


def main():  # Función principal
    sistema = SistemaGestion()  # Crea el sistema vacío
    print("=" * 70)  # Línea decorativa
    print("        SOFTWARE FJ - Sistema de Gestión de Clientes y Reservas")  # Título
    print("=" * 70)  # Línea decorativa

    # ---------- CLIENTES ----------
    ejecutar(1, "Registrar cliente válido (Ana Pérez)",  # Caso válido
             lambda: sistema.registrar_cliente("ana pérez", "1047123456", "ana.perez@correo.com", "3001234567"))
    ejecutar(2, "Registrar cliente válido (Luis Gómez)",  # Caso válido
             lambda: sistema.registrar_cliente("Luis Gómez", "73123456", "luisg@empresa.co", "3159876543"))
    ejecutar(3, "Registrar cliente con correo inválido",  # Caso inválido
             lambda: sistema.registrar_cliente("Marta Ruiz", "1002003004", "marta.correo", "3101112233"))
    ejecutar(4, "Registrar cliente con nombre con números",  # Caso inválido
             lambda: sistema.registrar_cliente("Carl0s 123", "1122334455", "carlos@mail.com", "3201112233"))
    ejecutar(5, "Registrar cliente duplicado (mismo documento de Ana)",  # Caso inválido
             lambda: sistema.registrar_cliente("Ana Otra", "1047123456", "otra@correo.com", "3007654321"))

    # ---------- SERVICIOS ----------
    ejecutar(6, "Crear servicio: Sala Ejecutiva",  # Caso válido
             lambda: sistema.agregar_servicio(ReservaSala("Sala Ejecutiva", 50000, capacidad=10)))
    ejecutar(7, "Crear servicio: Portátiles",  # Caso válido
             lambda: sistema.agregar_servicio(AlquilerEquipo("Portátiles", 15000, unidades=5)))
    ejecutar(8, "Crear servicio: Asesoría en Ciberseguridad",  # Caso válido
             lambda: sistema.agregar_servicio(Asesoria("Asesoría Ciberseguridad", 80000, "Seguridad informática", "experto")))
    ejecutar(9, "Crear servicio con tarifa negativa",  # Caso inválido
             lambda: sistema.agregar_servicio(ReservaSala("Sala Mala", -100, capacidad=5)))
    ejecutar(10, "Crear asesoría con nivel inexistente",  # Caso inválido
             lambda: sistema.agregar_servicio(Asesoria("Asesoría X", 60000, "Redes", "maestro")))
    ejecutar(11, "Crear servicio de proyectores sin unidades (queda no disponible)",  # Caso válido pero deshabilitado
             lambda: sistema.agregar_servicio(AlquilerEquipo("Proyectores", 10000, unidades=0)))

    # ---------- COTIZACIONES (sobrecarga) ----------
    sala = sistema.buscar_servicio("Sala Ejecutiva")  # Obtiene la sala para cotizar
    ejecutar(12, "Cotizar sala con un entero (4 horas)",  # Sobrecarga: int
             lambda: f"${sala.cotizar(4):,.2f}")
    ejecutar(13, "Cotizar sala con tupla (8 horas, 5 % descuento, con IVA)",  # Sobrecarga: tuple
             lambda: f"${sala.cotizar((8, 0.05)):,.2f}")
    ejecutar(14, "Cotizar sala con diccionario sin horas",  # Sobrecarga: dict con parámetro faltante
             lambda: sala.cotizar({"impuesto": 0.19}))
    ejecutar(15, "Cotizar sala con descuento del 150 % (cálculo inconsistente)",  # Error de cálculo
             lambda: sala.cotizar({"horas": 2, "descuento": 1.5}))

    # ---------- RESERVAS ----------
    reservas = {}  # Diccionario para guardar las reservas creadas y usarlas luego

    def crear_y_guardar(clave, *args, **kwargs):  # Función auxiliar que crea una reserva y la guarda
        reservas[clave] = sistema.crear_reserva(*args, **kwargs)  # Crea la reserva
        return reservas[clave]  # Devuelve la reserva

    ejecutar(16, "Reserva válida: Ana reserva la Sala Ejecutiva 3 h para 8 personas",  # Caso válido
             lambda: crear_y_guardar("r1", "1047123456", "Sala Ejecutiva", 3, personas=8))
    ejecutar(17, "Confirmar y procesar la reserva de Ana",  # Caso válido
             lambda: (reservas["r1"].confirmar(), f"Cobrado ${reservas['r1'].procesar():,.2f}")[1])
    ejecutar(18, "Reserva válida: Luis alquila 2 portátiles por 5 h",  # Caso válido
             lambda: crear_y_guardar("r2", "73123456", "Portátiles", 5, cantidad=2))
    ejecutar(19, "Procesar la reserva de Luis sin confirmarla",  # Operación no permitida
             lambda: reservas["r2"].procesar())
    ejecutar(20, "Cancelar la reserva de Luis",  # Caso válido
             lambda: (reservas["r2"].cancelar(), reservas["r2"].describir())[1])
    ejecutar(21, "Volver a cancelar la reserva ya cancelada",  # Operación no permitida
             lambda: reservas["r2"].cancelar())
    ejecutar(22, "Reserva de sala para 25 personas (supera la capacidad)",  # Reserva fallida
             lambda: sistema.crear_reserva("1047123456", "Sala Ejecutiva", 2, personas=25))
    ejecutar(23, "Reserva de un cliente que no existe",  # Reserva fallida
             lambda: sistema.crear_reserva("9999999", "Portátiles", 2))
    ejecutar(24, "Reserva de un servicio que no existe",  # Reserva fallida
             lambda: sistema.crear_reserva("73123456", "Impresora 3D", 2))
    ejecutar(25, "Reserva de Proyectores (servicio no disponible)",  # Reserva fallida
             lambda: sistema.crear_reserva("73123456", "Proyectores", 2))
    ejecutar(26, "Reserva sin indicar la duración",  # Parámetro faltante
             lambda: sistema.crear_reserva("73123456", "Asesoría Ciberseguridad", None))
    ejecutar(27, "Asesoría de Luis 2 h con 10 % de descuento",  # Caso válido completo
             lambda: (crear_y_guardar("r3", "73123456", "Asesoría Ciberseguridad", 2),
                      reservas["r3"].confirmar(),
                      f"Cobrado ${reservas['r3'].procesar(descuento=0.10):,.2f}")[2])
    ejecutar(28, "Calcular costo de sala con horas escritas como texto ('dos')",  # Dato de tipo incorrecto
             lambda: sala.calcular_costo("dos"))

    # ---------- RESUMEN ----------
    print("\n" + "=" * 70)  # Línea decorativa
    print("RESUMEN FINAL")  # Título del resumen
    for reserva in sistema.listar_reservas():  # Recorre todas las reservas
        print("  -", reserva)  # Muestra cada reserva
    datos = sistema.resumen()  # Obtiene los totales
    print(f"  Clientes: {datos['clientes']} | Servicios: {datos['servicios']} | Reservas: {datos['reservas']}")  # Totales
    print(f"  Total facturado: ${datos['facturado']:,.2f}")  # Dinero facturado
    print(f"  Operaciones exitosas: {resultados['exitosas']} | fallidas (controladas): {resultados['fallidas']}")  # Conteo
    print(f"  Log de eventos: {ARCHIVO_LOG}")  # Dónde quedó el log
    print("El sistema terminó sin interrupciones.")  # Mensaje final
    logger.info(f"=== Sistema finalizado: {datos} | {resultados} ===")  # Registra el cierre


if __name__ == "__main__":  # Solo se ejecuta si se corre este archivo directamente
    main()  # Llama a la función principal
