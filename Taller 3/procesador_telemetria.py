# INFRAESTRUCTURAS PARALELAS Y DISTRIBUIDAS-01 – TALLER 3
# Carlos Manuel Villamil Grisales – 2257751-3743

import queue
import random
import threading
import time


capacidad_buffer = 10
lecturas_por_productor = 10

num_productores = 3
num_consumidores = 2

umbral_temp = 85.0
umbral_presion = 100.0

buffer_telemetria = queue.Queue(maxsize=capacidad_buffer)

# lock para que los print de distintos hilos no se mezclen
lock_print = threading.Lock()

# estadisticas compartidas entre consumidores protegidas con lock
lock_stats = threading.Lock()
estadisticas = {
    "procesadas": 0,
    "alertas": 0,
    "por_consumidor": {},
}


def log(mensaje):
    with lock_print:
        print(mensaje)


def productor_sensores(id_productor):
    # genera lecturas y las mete en el buffer

    for i in range(1, lecturas_por_productor + 1):
        lectura = {
            "productor_id": id_productor,
            "sensor_id": f"s-{id_productor}0{random.randint(1, 5)}",
            "lectura_id": f"p{id_productor}-{i}",
            "temperatura": round(random.uniform(50.0, 100.0), 2),
            "presion": round(random.uniform(70.0, 120.0), 2),
        }

        # si el buffer esta lleno, put() bloquea hasta que haya espacio
        buffer_telemetria.put(lectura)

        log(
            f"[productor {id_productor}] "
            f"{lectura['lectura_id']} | "
            f"{lectura['sensor_id']} | "
            f"temp: {lectura['temperatura']}c | "
            f"presion: {lectura['presion']} psi | "
            f"buffer: {buffer_telemetria.qsize()}/{capacidad_buffer}"
        )

        time.sleep(random.uniform(0.05, 0.2))

    log(f"[productor {id_productor}] termino")


def consumidor_alertas(id_consumidor):
    #lee las lecturas y revisa si hay valores altos

    procesadas = 0
    alertas = 0

    while True:
        # si el buffer esta vacio, get() bloquea hasta que llegue algo
        lectura = buffer_telemetria.get()

        # None es la senal de parada (una por consumidor)
        if lectura is None:
            buffer_telemetria.task_done()
            break

        temp_alta = lectura["temperatura"] > umbral_temp
        presion_alta = lectura["presion"] > umbral_presion

        if temp_alta or presion_alta:
            alertas += 1
            log(
                f"    [consumidor {id_consumidor}] alerta | "
                f"{lectura['lectura_id']} | "
                f"{lectura['sensor_id']} | "
                f"temp: {lectura['temperatura']}c | "
                f"presion: {lectura['presion']} psi"
            )
        else:
            log(
                f"    [consumidor {id_consumidor}] ok | "
                f"{lectura['lectura_id']} | "
                f"lectura normal: {lectura['sensor_id']}"
            )

        procesadas += 1
        buffer_telemetria.task_done()
        time.sleep(random.uniform(0.1, 0.25))

    with lock_stats:
        estadisticas["procesadas"] += procesadas
        estadisticas["alertas"] += alertas
        estadisticas["por_consumidor"][id_consumidor] = procesadas

    log(f"    [consumidor {id_consumidor}] termino ({procesadas} lecturas)")


if __name__ == "__main__":
    print(
        f"iniciando monitoreo con {num_productores} productores "
        f"y {num_consumidores} consumidores..."
    )
    inicio = time.time()

    productores = [
        threading.Thread(
            target=productor_sensores,
            args=(i,),
            name=f"productor-{i}"
        )
        for i in range(1, num_productores + 1)
    ]

    consumidores = [
        threading.Thread(
            target=consumidor_alertas,
            args=(i,),
            name=f"consumidor-{i}"
        )
        for i in range(1, num_consumidores + 1)
    ]

    for hilo in productores + consumidores:
        hilo.start()

    # primero se espera a que todos los productores terminen
    for hilo in productores:
        hilo.join()

    # luego se manda una señal de parada por cada consumidor.
    # si cada productor mandara su propio None, un consumidor podria
    # detenerse antes de tiempo mientras otros productores siguen generando.
    for _ in consumidores:
        buffer_telemetria.put(None)

    for hilo in consumidores:
        hilo.join()

    duracion = time.time() - inicio
    total_esperado = num_productores * lecturas_por_productor

    print("\n--- resumen ---")
    print(f"lecturas generadas: {total_esperado}")
    print(f"lecturas procesadas: {estadisticas['procesadas']}")
    print(f"alertas detectadas: {estadisticas['alertas']}")
    for id_consumidor, cantidad in sorted(estadisticas["por_consumidor"].items()):
        print(f"  consumidor {id_consumidor}: {cantidad} lecturas")
    print(f"tiempo total: {duracion:.2f} s")
    print("monitoreo terminado")
