from abc import ABC, abstractmethod
import logging

# Guarda los eventos y errores en un archivo
logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class DatoInvalidoError(Exception):
    pass


class ReservaError(Exception):
    pass


class Entidad(ABC):
    def __init__(self, codigo):
        self.codigo = codigo

    @abstractmethod
    def mostrar_datos(self):
        pass


class Cliente(Entidad):
    def __init__(self, codigo, nombre, correo):
        super().__init__(codigo)

        if nombre == "" or "@" not in correo:
            raise DatoInvalidoError("Nombre o correo incorrecto")

        self.__nombre = nombre
        self.__correo = correo

    def mostrar_datos(self):
        return f"Cliente: {self.__nombre} - {self.__correo}"

    def obtener_nombre(self):
        return self.__nombre


class Servicio(Entidad):
    def __init__(self, codigo, nombre, precio):
        super().__init__(codigo)

        if precio <= 0:
            raise DatoInvalidoError("El precio debe ser mayor que cero")

        self.nombre = nombre
        self.precio = precio

    def calcular_costo(self, cantidad=1, impuesto=0, descuento=0):
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad debe ser mayor que cero")

        total = self.precio * cantidad
        total = total - (total * descuento)
        total = total + (total * impuesto)
        return round(total, 2)

    @abstractmethod
    def mostrar_datos(self):
        pass


class ReservaSala(Servicio):
    def mostrar_datos(self):
        return f"Sala: ${self.precio} por hora"


class AlquilerEquipo(Servicio):
    def mostrar_datos(self):
        return f"Alquiler de equipo: ${self.precio} por día"


class Asesoria(Servicio):
    def mostrar_datos(self):
        return f"Asesoría: ${self.precio} por hora"


class Reserva(Entidad):
    def __init__(self, codigo, cliente, servicio, cantidad):
        super().__init__(codigo)

        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad debe ser mayor que cero")

        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.estado = "Pendiente"

    def confirmar(self):
        self.estado = "Confirmada"
        logging.info("Reserva %s confirmada", self.codigo)
        return "Reserva confirmada"

    def cancelar(self):
        if self.estado == "Procesada":
            raise ReservaError("No se puede cancelar una reserva procesada")

        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada", self.codigo)
        return "Reserva cancelada"

    def procesar(self):
        if self.estado != "Confirmada":
            raise ReservaError("Primero debe confirmar la reserva")

        try:
            total = self.servicio.calcular_costo(
                self.cantidad, impuesto=0.19, descuento=0.10
            )
        except Exception as error:
            logging.error("Error al calcular la reserva")
            raise ReservaError("No se pudo calcular el costo") from error

        self.estado = "Procesada"
        logging.info("Reserva %s procesada", self.codigo)
        return round(total, 2)

    def mostrar_datos(self):
        return (
            f"Reserva {self.codigo} - Cliente: "
            f"{self.cliente.obtener_nombre()} - "
            f"Servicio: {self.servicio.nombre} - Estado: {self.estado}"
        )


class Sistema:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def agregar_cliente(self, cliente):
        self.clientes.append(cliente)
        logging.info("Cliente agregado")
        return "Cliente registrado"

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)
        logging.info("Servicio agregado")
        return "Servicio registrado"

    def agregar_reserva(self, reserva):
        self.reservas.append(reserva)
        logging.info("Reserva agregada")
        return "Reserva creada"


def probar(numero, descripcion, funcion):
    print(f"\nOperación {numero}: {descripcion}")
    try:
        resultado = funcion()
        print(resultado)
    except (DatoInvalidoError, ReservaError) as error:
        logging.error("Operación %s: %s", numero, error)
        print("Error controlado:", error)
    except Exception as error:
        logging.exception("Error inesperado")
        print("Error inesperado:", error)
    else:
        print("Operación realizada correctamente")
    finally:
        print("El programa continúa.")


def main():
    sistema = Sistema()

    cliente1 = Cliente("C1", "Ana Pérez", "ana@gmail.com")
    cliente2 = Cliente("C2", "Luis Gómez", "luis@gmail.com")

    sala = ReservaSala("S1", "Reserva de sala", 50000)
    equipo = AlquilerEquipo("S2", "Alquiler de computador", 80000)
    asesoria = Asesoria("S3", "Asesoría de programación", 60000)

    probar(1, "Registrar cliente Ana", lambda: sistema.agregar_cliente(cliente1))
    probar(2, "Registrar cliente Luis", lambda: sistema.agregar_cliente(cliente2))
    probar(
        3,
        "Registrar cliente con correo incorrecto",
        lambda: sistema.agregar_cliente(Cliente("C3", "Carlos", "correo-malo")),
    )
    probar(4, "Registrar servicio de sala", lambda: sistema.agregar_servicio(sala))
    probar(5, "Registrar alquiler de equipo", lambda: sistema.agregar_servicio(equipo))
    probar(6, "Registrar asesoría", lambda: sistema.agregar_servicio(asesoria))
    probar(7, "Crear reserva con duración incorrecta", lambda: Reserva("R1", cliente1, sala, 0))

    reserva1 = Reserva("R2", cliente1, sala, 2)
    probar(8, "Crear reserva válida", lambda: sistema.agregar_reserva(reserva1))

    def confirmar_y_calcular():
        reserva1.confirmar()
        return "Total a pagar: $" + str(reserva1.procesar())

    probar(9, "Confirmar y procesar reserva", confirmar_y_calcular)

    reserva2 = Reserva("R3", cliente2, asesoria, 1)
    probar(10, "Procesar reserva sin confirmar", lambda: reserva2.procesar())
if __name__ == "__main__":
    main()
