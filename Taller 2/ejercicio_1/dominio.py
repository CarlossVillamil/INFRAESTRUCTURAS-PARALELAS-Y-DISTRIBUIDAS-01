import os
import time
from PIL import Image
import multiprocessing

def convertir_a_gris(lista_imagenes, inicio, fin):

    for i in range(inicio, fin):
        ruta_imagen = lista_imagenes[i]
        try:
            imagen = Image.open(ruta_imagen)
            imagen_gris = imagen.convert('L')  # 'L' representa escala de grises
            nombre_archivo, extension = os.path.splitext(ruta_imagen)
            ruta_gris = nombre_archivo + "_gris" + extension
            imagen_gris.save(ruta_gris)
            print(f"Imagen convertida: {ruta_imagen} -> {ruta_gris}")
        except FileNotFoundError:
            print(f"Error: No se encontró la imagen {ruta_imagen}")
        except Exception as e:
            print(f"Error al procesar {ruta_imagen}: {e}")

def procesar_imagenes_paralelo(lista_imagenes):
    
    #Procesa las imágenes dividiendo manualmente la lista según la cantidad de núcleos

    num_procesos = multiprocessing.cpu_count()  
    tamano_porcion = len(lista_imagenes) // num_procesos
    
    procesos = []

    # 1. Crear y lanzar los procesos
    for i in range(num_procesos):
        # Calcular los índices de la porción correspondiente a este proceso
        inicio_porcion = i * tamano_porcion
        # El último proceso toma hasta el final de la lista para no dejar elementos por fuera
        fin_porcion = (i + 1) * tamano_porcion if i < num_procesos - 1 else len(lista_imagenes)
        
        # Crear el proceso asignando el rango específico de datos
        p = multiprocessing.Process(target=convertir_a_gris, args=(lista_imagenes, inicio_porcion, fin_porcion))
        procesos.append(p)
        p.start()

    # 2. Esperar a que todos los procesos terminen
    for p in procesos:
        p.join()



if __name__ == '__main__':
    directorio_imagenes = "imagenes_prueba_dom"  # Reemplaza con el nombre de tu directorio
    lista_imagenes = [
        os.path.join(directorio_imagenes, f)
        for f in os.listdir(directorio_imagenes)
        if os.path.isfile(os.path.join(directorio_imagenes, f))
    ]
    inicio = time.time()
    procesar_imagenes_paralelo(lista_imagenes)
    fin = time.time()
    print(f"Tiempo total de procesamiento paralelo: {fin - inicio:.2f} segundos")