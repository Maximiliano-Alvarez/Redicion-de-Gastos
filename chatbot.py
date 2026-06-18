import csv
import re

# ============================================================
#   FUNCIONES DE BASE DE DATOS
# ============================================================

def cargar_datos():
    with open("empleados.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def guardar_datos(datos):
    with open("empleados.csv", "w", newline="", encoding="utf-8") as f:
        campos = ["legajo","nombre","dni","viaticos","comida","transporte","insumos"]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(datos)

# ============================================================
#   FUNCIONES DE UTILIDAD
# ============================================================

def limpiar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"[^a-záéíóúñ0-9 ]", "", texto)
    return texto.strip()

def detectar_intencion(texto):
    texto = limpiar_texto(texto)

    # Intenciones de carga de gasto
    if any(p in texto for p in [
        "cargar gasto", "registrar gasto", "tengo un gasto", "quiero cargar",
        "puedo gastar", "me alcanza", "si gasto", "quiero gastar"
    ]):
        return "cargar_gasto"

    # Intenciones de consulta de fondos
    if any(p in texto for p in [
        "cuanto tengo", "fondos", "saldo", "cuanto me queda", "ver fondos"
    ]):
        return "consultar_fondos"

    # Saludos
    if any(p in texto for p in ["hola", "buenas", "hey", "que tal"]):
        return "saludo"

    # Despedidas
    if any(p in texto for p in ["adios", "chau", "nos vemos", "hasta luego"]):
        return "despedida"

    return "desconocido"

def buscar_empleado(identificador, datos):
    identificador = identificador.lower()
    for emp in datos:
        if (emp["legajo"].lower() == identificador or
            emp["dni"].lower() == identificador or
            emp["nombre"].lower() == identificador):
            return emp
    return None

def extraer_categoria(texto):
    texto = limpiar_texto(texto)

    categorias = {
        "viaticos": ["viatico", "viaticos", "viaje"],
        "comida": ["comida", "almuerzo", "cena", "desayuno"],
        "transporte": ["transporte", "taxi", "colectivo", "uber"],
        "insumos": ["insumos", "materiales", "utiles"]
    }

    for categoria, palabras in categorias.items():
        for p in palabras:
            if p in texto:
                return categoria

    return None

def extraer_monto(texto):
    # SOLO números, nada de palabras
    numeros = re.findall(r"\d+\.?\d*", texto)
    if numeros:
        return float(numeros[0])
    return None

# ============================================================
#   FUNCIONES DE INTENCIÓN
# ============================================================

def procesar_saludo(nombre):
    print(f"🤖 Hola {nombre}! ¿Qué necesitás hoy?")

def procesar_despedida(nombre):
    print(f"🤖 ¡Hasta luego {nombre}! Gracias por usar el Chatbot de OE.")

def procesar_consulta_fondos(mensaje, empleado):
    categoria = extraer_categoria(mensaje)

    if categoria is None:
        print("🤖 ¿De qué categoría querés saber el fondo? (viaticos, comida, transporte, insumos)")
        return

    fondo = float(empleado[categoria])
    print(f"💰 {empleado['nombre']}, tenés ${fondo} disponibles en {categoria}.")

def procesar_carga_gasto(mensaje, empleado, datos):
    categoria = extraer_categoria(mensaje)
    monto = extraer_monto(mensaje)

    # Si no detectó categoría
    if categoria is None:
        categoria = input("🤖 ¿En qué categoría es el gasto?: ").lower()
        if extraer_categoria(categoria) is None:
            print("❌ Esa categoría no existe.")
            return
        categoria = extraer_categoria(categoria)

    # Si no detectó monto
    if monto is None:
        monto = input("🤖 ¿De cuánto es el gasto? (solo números): ")
        try:
            monto = float(monto)
        except:
            print("❌ Ese monto no es válido.")
            return

    fondo_actual = float(empleado[categoria])
    fondo_restante = fondo_actual - monto

    print(f"💰 Fondos disponibles en {categoria}: ${fondo_actual}")

    # CASO 1 — Puede hacer el gasto y le queda dinero
    if fondo_restante > 0:
        print(f"✔ {empleado['nombre']}, podés hacer este gasto.")
        print(f"💵 Si lo hacés, te van a quedar ${fondo_restante} en {categoria}.")
        
        # Actualizar CSV
        for emp in datos:
            if emp["legajo"] == empleado["legajo"]:
                emp[categoria] = str(fondo_restante)
        guardar_datos(datos)
        empleado[categoria] = str(fondo_restante)

    # CASO 2 — Puede hacer el gasto pero le queda EXACTAMENTE 0
    elif fondo_restante == 0:
        print(f"⚠ {empleado['nombre']}, podés hacer el gasto, pero te quedarías SIN fondos en {categoria}.")
        
        # Actualizar CSV
        for emp in datos:
            if emp["legajo"] == empleado["legajo"]:
                emp[categoria] = "0"
        guardar_datos(datos)
        empleado[categoria] = "0"

    # CASO 3 — No puede hacer el gasto
    else:
        print(f"❌ {empleado['nombre']}, no podés hacer este gasto.")
        print(f"Te faltan ${abs(fondo_restante)} para poder cubrirlo.")

# ============================================================
#   EJECUCIÓN DIRECTA DEL CHATBOT
# ============================================================

print("🤖 Hola! Soy el Chatbot de OE. Antes de empezar, necesito identificarte.")
print("Escribí 'salir' para terminar.")

datos = cargar_datos()
empleado = None

# IDENTIFICACIÓN
while empleado is None:
    ident = input("\n👉 Decime tu legajo, nombre o DNI: ")

    if ident.lower() == "salir":
        print("👋 ¡Hasta luego!")
        exit()

    empleado = buscar_empleado(ident, datos)

    if empleado:
        print(f"✔ Perfecto {empleado['nombre']}, ya estás identificado.")
    else:
        print("❌ No encontré ese empleado. Probá de nuevo.")

nombre = empleado["nombre"]

print(f"\n🤖 ¿En qué puedo ayudarte hoy, {nombre}?")

# LOOP PRINCIPAL
while True:
    mensaje = input(f"\n{nombre}: ")

    if mensaje.lower() == "salir":
        procesar_despedida(nombre)
        break

    intencion = detectar_intencion(mensaje)

    if intencion == "saludo":
        procesar_saludo(nombre)

    elif intencion == "despedida":
        procesar_despedida(nombre)
        break

    elif intencion == "consultar_fondos":
        procesar_consulta_fondos(mensaje, empleado)

    elif intencion == "cargar_gasto":
        procesar_carga_gasto(mensaje, empleado, datos)

    else:
        print(f"🤖 No entendí lo que quisiste decir, {nombre}. Podés decir cosas como:")
        print("   - 'quiero cargar un gasto'")
        print("   - 'cuánto me queda en viáticos'")
        print("   - 'tengo un gasto de 500 en comida'")
        print("   - 'quiero ver mis fondos'")
