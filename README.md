# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto de la Fase 4 del curso **Programación (213023)** de la UNAD.
Sistema orientado a objetos en Python, **sin base de datos**, que gestiona clientes,
servicios (salas, alquiler de equipos y asesorías) y reservas, con manejo avanzado
de excepciones y registro de eventos en un archivo de logs.

## Cómo ejecutarlo

Requiere Python 3.8 o superior. No necesita librerías externas.

```bash
python main.py
```

Al terminar, los eventos y errores quedan en `logs/software_fj.log`.

## Estructura

| Archivo | Contenido |
|---|---|
| `excepciones.py` | Jerarquía de excepciones personalizadas (`SoftwareFJError` y sus hijas) |
| `registro_logs.py` | Configuración del archivo de logs |
| `entidades.py` | Clase abstracta `Entidad` y clase `Cliente` (encapsulación y validaciones) |
| `servicios.py` | Clase abstracta `Servicio` y sus hijas `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| `reservas.py` | Clase `Reserva` (confirmar, cancelar, procesar) |
| `sistema.py` | Clase `SistemaGestion`, que guarda todo en listas internas |
| `main.py` | Simulación de 28 operaciones válidas e inválidas |

## Conceptos aplicados

- **Abstracción:** `Entidad` y `Servicio` son clases abstractas (`ABC`, `@abstractmethod`).
- **Herencia:** `Cliente`, `Servicio` y `Reserva` heredan de `Entidad`, y los tres servicios heredan de `Servicio`.
- **Polimorfismo:** cada servicio sobrescribe `calcular_costo()`, `describir()` y `validar_parametros()`.
- **Encapsulación:** los datos del cliente son privados (`__nombre`, `__documento`...) y se validan con `@property`.
- **Sobrecarga:** `Servicio.cotizar()` usa `functools.singledispatchmethod` y responde distinto si recibe un `int`, una `tuple` o un `dict`. Python no tiene sobrecarga nativa, por eso se usa esta herramienta, además de los parámetros opcionales de `calcular_costo(horas, impuesto=0.0, descuento=0.0, **parametros)`.
- **Excepciones:** excepciones propias, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento con `raise ... from ...`.
- **Logs:** todos los eventos y errores se registran con el módulo `logging`.
