# Simulador base del SLS

import os
import time

os.system("cls" if os.name == "nt" else "clear")

historial = []


# -----------------------------
# Funciones del sistema
# -----------------------------

def es_instruccion(linea):
	return (
		linea.endswith("@") or
		(linea.startswith("gt") and "@" in linea) or
		(linea.startswith("R") and "@" in linea) or
		(linea.startswith("del") and "@" in linea) or
		(linea.startswith("imp@"))
	)

runent = False # Variable global para controlar el modo runent
ultima_importacion = [] # Variable global para almacenar la última importación

def ejecutar_instruccion(linea):
	global historial
	global runent

	if linea == "runent@":	
		runent = not runent
		print(f"Modo runent {'activado' if runent else 'desactivado'}")
		return None
	
	# ---- EXIT ----
	if linea == "exit@":
		print("Saliendo del programa...")
		return "exit"

	# ---- CLEAN ----
	if linea == "cls@":
		os.system("cls" if os.name == "nt" else "clear")
		return None
	
	if linea == "res@":
		os.system("cls" if os.name == "nt" else "clear")
		historial = []
		return None
	
	if linea == "imps@":
		os.system("cls" if os.name == "nt" else "clear")
		historial = ultima_importacion.copy()  # Restaurar el historial a la última importación
		for i, l in enumerate(historial):
			print(f"{i} => {l}")
		return None

	# ---- HIST ----
	if linea == "hist@":
		print("Historial:")
		for i, l in enumerate(historial):
			print(f"{i} => {l}")
		return None

	# ---- GOTO ----
	if linea.startswith("gt") and "@" in linea:
		try:
			parte = linea[2:]
			indice_str, nuevo = parte.split("@", 1)
			indice = int(indice_str)

			if 0 <= indice < len(historial):
				historial[indice] = nuevo

				os.system("cls" if os.name == "nt" else "clear")

				#Historial actualizado
				for i, l in enumerate(historial):
					print(f"{i} => {l}")
			else:
				print("Índice fuera de rango")

		except:
			print("Formato inválido. Usa: goto<número>@<texto>")

		return None

	# ---- DEL ----
	if linea.startswith("del") and "@" in linea:
		try:
			num_str = linea[3:-1]
			indice = int(num_str)

			if 0 <= indice < len(historial):
				del historial[indice]

				os.system("cls" if os.name == "nt" else "clear")

				#Historial actualizado
				for i, l in enumerate(historial):
					print(f"{i} => {l}")
			else:
				print("Índice fuera de rango")

		except:
			print("Formato inválido. Usa: del<número>@")

		return None

	# ---- r@ ----
	if linea == "r@":
		os.system("cls" if os.name == "nt" else "clear")
		ejecutar_sistema(1)
		return None

	# ---- R<n>@ ----
	if linea.startswith("R"):
		try:
			
			n, velocidad = map(int, linea[1:].split("@"))

			os.system("cls" if os.name == "nt" else "clear")

			ejecutar_sistema(n, veces_por_segundo=velocidad)
		except:
			print("Formato inválido. Usa: R<número>@")
		return None

	# ---- IMPORTAR ----
	if linea.startswith("imp@"):
		try:
			nombre = linea[4:] + ".txt"  # después de "imp@" + .txt
			#para la importacion RELATIVA de archivos
			BASE_DIR = os.path.dirname(__file__)

			#"C:\Users\edgar\Documents\PrPython\SistemaSustitucion\main.py"
			with open(os.path.join(BASE_DIR, nombre), "r", encoding="utf-8") as f:
				lineas = f.readlines()

			for l in lineas:
				l = l.strip()
				if l != "":
					historial.append(l)

			os.system("cls" if os.name == "nt" else "clear")

			print("Archivo importado correctamente.")
			#"Historial actualizado:"

			for i, l in enumerate(historial):
				print(f"{i} => {l}")
			ultima_importacion = historial[-len(lineas):]  # Obtener las líneas recién importadas

		except:
			print("Error al importar archivo.")

		return None
	
	print("Instrucción desconocida")
	return None

# -----------------------------
# Motor de ejecución
# -----------------------------

def aplicar_reglas(texto, reglas):
	def match_flattened(start, L):
		pos = start
		matched = 0
		stack = []
		while pos < len(texto) and matched < len(L):
			if texto[pos] == "(":
				stack.append("(")
				pos += 1
				continue
			if texto[pos] == ")":
				if stack:
					stack.pop()
				pos += 1
				continue
			if texto[pos] != L[matched]:
				return None
			matched += 1
			pos += 1
		if matched != len(L):
			return None
		while pos < len(texto) and stack:
			if texto[pos] == "(":
				stack.append("(")
			elif texto[pos] == ")":
				stack.pop()
			pos += 1
		return pos if not stack else None

	resultado = ""
	i = 0
	while i < len(texto):
		aplicado = False

		# Reemplazo especial para paréntesis completo con coincidencia exacta del contenido.
		if texto[i] == "(":
			profundidad = 1
			j = i + 1
			while j < len(texto) and profundidad > 0:
				if texto[j] == "(":
					profundidad += 1
				elif texto[j] == ")":
					profundidad -= 1
				j += 1

			if profundidad == 0:
				contenido = texto[i+1:j-1]
				for regla in reglas:
					if ">" in regla:
						partes = regla.split(">", 1)
						L = partes[0]
						R = partes[1]
						if L == contenido:
							resultado += R
							i = j
							aplicado = True
							break
				if aplicado:
					continue
				resultado += texto[i:j]
				i = j
				continue

		for regla in reglas:
			if ">" in regla:
				partes = regla.split(">", 1)
				L = partes[0]
				R = partes[1]
				if L == "":
					continue
				if i + len(L) <= len(texto) and texto[i:i+len(L)] == L:
					resultado += R
					i += len(L)
					aplicado = True
					break
				end = match_flattened(i, L)
				if end is not None:
					resultado += R
					i = end
					aplicado = True
					break
		if not aplicado:
			resultado += texto[i]
			i += 1
	return resultado


def reemplazo_simple(texto, L, R):
	resultado = ""
	i = 0

	while i < len(texto):
		if i + len(L) <= len(texto) and texto[i:i+len(L)] == L:
			resultado += R
			i += len(L)
		else:
			resultado += texto[i]
			i += 1

	return resultado


def recolectar_reglas(historial):
	reglas = []
	for linea in historial:
		if ">" in linea:
			# Si la regla está delimitada por paréntesis (A>B), extraer el contenido
			if linea.startswith("(") and linea.endswith(")"):
				contenido = linea[1:-1]
				if ">" in contenido:
					reglas.append(contenido)
			else:
				reglas.append(linea)
	return reglas


def ejecutar_sistema(veces, veces_por_segundo=0):
	global historial

	for paso in range(veces):
		reglas = recolectar_reglas(historial)

		os.system("cls" if os.name == "nt" else "clear")
		print(f"Ejecución {paso + 1}:")

		nuevo_historial = []

		for i in range(len(historial)):
			resultado = aplicar_reglas(historial[i], reglas)
			nuevo_historial.append(resultado)
			print(f"{i} => {resultado}")

		historial = nuevo_historial
		if veces_por_segundo > 0:
			time.sleep(1 / veces_por_segundo)  # Pausa entre ejecuciones


# -----------------------------
# Bucle principal
# -----------------------------

while True:
	entrada = str(input(f"{len(historial)} => "))

	if runent and entrada == "":
		os.system("cls" if os.name == "nt" else "clear")
		ejecutar_sistema(1)
		continue

	if es_instruccion(entrada):
		resultado = ejecutar_instruccion(entrada)
		if resultado == "exit":
			break
		continue

	historial.append(entrada)