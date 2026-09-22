import time
import multiprocessing

# Cada mensaje contiene varias líneas para reducir el coste de IPC.
TAMANO_LOTE = 10000


def leer_archivo(ruta_entrada, cola_salida):
    
    # Lee el archivo línea por línea y envía cada línea a la siguiente etapa.
    try:
        with open(ruta_entrada, 'r') as f_in:
            lote = []
            for linea in f_in:
                lote.append(linea)
                if len(lote) == TAMANO_LOTE:
                    cola_salida.put(lote)
                    lote = []
            if lote:
                cola_salida.put(lote)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_entrada}")
    finally:
        cola_salida.put(None)

# tarea limpiar
def limpiar_linea(cola_entrada, cola_salida):

    # Toma líneas de la cola de entrada y las limpia
    while True:
        lote = cola_entrada.get()
        if lote is None:
            # señal de fin, la pasamos adelante y terminamos
            cola_salida.put(None)
            break
        
        cola_salida.put([linea.strip() for linea in lote])

# tarea convertir a mayus
def convertir_mayusculas(cola_entrada, cola_salida):

    # toma líneas de la cola de entrada, las convierte a mayúsculas y las envía a la cola de salida
    while True:
        lote = cola_entrada.get()
        if lote is None:
            cola_salida.put(None)
            break
        
        cola_salida.put([linea.upper() for linea in lote])

# tarea escribir
def escribir_archivo(ruta_salida, cola_entrada):
    
    # Toma las líneas procesadas finales y las escribe en el archivo de salida.
    with open(ruta_salida, 'w') as f_out:
        while True:
            lote = cola_entrada.get()
            if lote is None:
                break 
            
            f_out.write('\n'.join(lote) + '\n')

#configuración del pipeline
def procesar_texto_pipeline(ruta_entrada, ruta_salida):

    # crear colas
    cola_leer_limpiar = multiprocessing.Queue()
    cola_limpiar_mayus = multiprocessing.Queue()
    cola_mayus_escribir = multiprocessing.Queue()

    # definir procesos cada etapa
    p_leer = multiprocessing.Process(target=leer_archivo, args=(ruta_entrada, cola_leer_limpiar))
    p_limpiar = multiprocessing.Process(target=limpiar_linea, args=(cola_leer_limpiar, cola_limpiar_mayus))
    p_mayus = multiprocessing.Process(target=convertir_mayusculas, args=(cola_limpiar_mayus, cola_mayus_escribir))
    p_escribir = multiprocessing.Process(target=escribir_archivo, args=(ruta_salida, cola_mayus_escribir))

    # inciar los procesos
    p_leer.start()
    p_limpiar.start()
    p_mayus.start()
    p_escribir.start()

    # esperar a que todos los procesos terminen
    p_leer.join()
    p_limpiar.join()
    p_mayus.join()
    p_escribir.join()

if __name__ == '__main__':

    ruta_entrada = "texto_entrada.txt"
    ruta_salida = "texto_salida_pipeline.txt"
    
    inicio = time.time()
    procesar_texto_pipeline(ruta_entrada, ruta_salida)
    fin = time.time()
    
    print(f"Tiempo total de procesamiento pipeline paralelo: {fin - inicio:.2f} segundos")
    print(f"Archivo procesado guardado en {ruta_salida}")


