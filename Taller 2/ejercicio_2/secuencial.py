import time


def procesar_texto_secuencial(ruta_entrada, ruta_salida):
	"""Procesa el archivo de texto secuencialmente."""
	try:
		with open(ruta_entrada, 'r') as f_in, open(ruta_salida, 'w') as f_out:
			for linea in f_in:
				linea_limpia = linea.strip()
				linea_mayusculas = linea_limpia.upper()
				f_out.write(linea_mayusculas + '\n')
	except FileNotFoundError:
		print(f"Error: No se encontró el archivo {ruta_entrada}")


if __name__ == '__main__':
	ruta_entrada = "texto_entrada.txt"
	ruta_salida = "texto_salida_secuencial.txt"
	inicio = time.time()
	procesar_texto_secuencial(ruta_entrada, ruta_salida)
	fin = time.time()
	print(f"Tiempo total de procesamiento secuencial: {fin - inicio:.2f} segundos")
	print(f"Archivo procesado secuencialmente guardado en {ruta_salida}")