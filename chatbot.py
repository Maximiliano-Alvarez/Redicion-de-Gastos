import csv
import re
import unicodedata

# ============================================================
#   FUNCIONES DE BASE DE DATOS
# ============================================================

def cargar_datos():
    """
    Lee el archivo empleados.csv y devuelve una lista de diccionarios,
    uno por cada empleado (cada fila del CSV).
    Esto actúa como nuestra "base de datos" en memoria.
    """
    with open("empleados.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def guardar_datos(datos):
    """
    Sobrescribe empleados.csv con la lista de diccionarios actualizada.
    Se llama cada vez que se confirma un gasto, para persistir el cambio
    en disco (si no se llamara, el cambio se perdería al cerrar el programa).
    """
    with open("empleados.csv", "w", newline="", encoding="utf-8") as f:
        campos = ["legajo","nombre","dni","viaticos","comida","transporte","insumos"]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(datos)

# ============================================================
#   FUNCIONES DE UTILIDAD
# ============================================================

def es_confirmacion(texto):
    """
    Determina si el texto ingresado por el usuario equivale a un "sí".
    Se compara contra una lista de variantes comunes en español rioplatense
    (incluye "dale", "ok", "sip", etc.), no solo "si"/"no" literales.
    """
    texto = limpiar_texto(texto)
    confirmaciones = [
        "si", "sí", "dale", "ok", "confirmo",
        "sip", "si por favor", "si porfavor",
        "por favor", "si dale", "si dale ok",
        "si ok", "si, por favor"
    ]
    return texto in confirmaciones


def limpiar_texto(texto):
    """
    Normaliza un texto para que las comparaciones de palabras clave
    funcionen de forma consistente, sin importar mayúsculas, tildes
    o signos de puntuación.

    Pasos:
    1) Pasa todo a minúsculas.
    2) Descompone los caracteres acentuados en su letra base + acento
       (NFD) y luego elimina el acento, convirtiendo por ejemplo
       "viático" en "viatico". Esto evita que "cuánto" no matchee
       contra "cuanto" en las listas de palabras clave.
    3) Elimina cualquier carácter que no sea letra, número o espacio
       (signos de pregunta, comas, etc.).
    """
    texto = texto.lower()

    # Normalizar acentos: "á" → "a"
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")

    # Mantener solo letras, números y espacios
    texto = re.sub(r"[^a-z0-9 ]", "", texto)

    return texto.strip()

def detectar_intencion(texto):
    """
    Clasifica el mensaje del usuario en una de cuatro intenciones
    posibles (cargar_gasto, consultar_fondos, saludo, despedida)
    según si contiene alguna de las frases/palabras clave asociadas.
    Si no coincide con ninguna, devuelve "desconocido".

    Es un enfoque de reconocimiento de intención por keyword matching:
    simple y predecible, pero no entiende sinónimos no listados.
    """
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
    """
    Busca, dentro de la lista de empleados cargada del CSV, uno cuyo
    legajo, DNI o nombre coincida exactamente (sin distinguir mayúsculas)
    con el identificador ingresado. Devuelve el diccionario del empleado
    encontrado, o None si no hay coincidencia.
    """
    identificador = identificador.lower()
    for emp in datos:
        if (emp["legajo"].lower() == identificador or
            emp["dni"].lower() == identificador or
            emp["nombre"].lower() == identificador):
            return emp
    return None

def extraer_categoria(texto):
    """
    Busca dentro del texto alguna palabra asociada a una categoría de
    gasto (viaticos, comida, transporte, insumos) y devuelve el nombre
    de esa categoría. Si no encuentra ninguna, devuelve None.

    El diccionario "categorias" funciona como un mapa de sinónimos:
    por ejemplo, "taxi", "colectivo" o "uber" todos apuntan a "transporte".
    """
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
    """
    Extrae el primer número que aparece en el texto e intenta
    convertirlo a float, respetando el formato numérico argentino
    (punto como separador de miles, coma como separador decimal).

    Ejemplos de conversión:
      "1.500,75" -> 1500.75
      "2.000"    -> 2000.0
      "1500,5"   -> 1500.5

    Si no encuentra ningún número, o el número no se puede convertir,
    devuelve None.
    """
    # Buscar números con coma o punto
    numeros = re.findall(r"\d[\d\.,]*", texto)

    if not numeros:
        return None

    numero = numeros[0]

    # Normalizar formato argentino:
    # 1.500,75 → 1500.75
    # 2.000 → 2000
    # 1500,5 → 1500.5
    numero = numero.replace(".", "")      # eliminar separador de miles
    numero = numero.replace(",", ".")     # convertir coma decimal a punto

    try:
        return float(numero)
    except:
        return None

# ============================================================
#   FUNCIONES DE INTENCIÓN
# ============================================================
# Cada función de esta sección ejecuta la acción correspondiente
# a una intención ya detectada. Reciben los datos que necesitan
# (mensaje, empleado, lista completa de datos) y se encargan de
# imprimir la respuesta del bot y, si corresponde, actualizar el CSV.

def procesar_saludo(nombre):
    """Responde a un saludo del empleado."""
    print(f"🤖 Hola {nombre}! ¿Qué necesitás hoy?")

def procesar_despedida(nombre):
    """Responde a una despedida del empleado (también corta el bucle principal)."""
    print(f"🤖 ¡Hasta luego {nombre}! Gracias por usar el Chatbot de OE.")

def procesar_consulta_fondos(mensaje, empleado):
    """
    Informa el saldo disponible en una categoría determinada.
    Si el mensaje no menciona ninguna categoría reconocible,
    le pide al usuario que aclare cuál quiere consultar y no
    imprime ningún saldo (queda pendiente de resolverse en el
    bucle principal mediante "esperando_categoria").
    """
    categoria = extraer_categoria(mensaje)

    if categoria is None:
        print("🤖 ¿De qué categoría querés saber el fondo? (viaticos, comida, transporte, insumos)")
        return

    fondo = float(empleado[categoria])
    print(f"💰 {empleado['nombre']}, tenés ${fondo} disponibles en {categoria}.")

def procesar_carga_gasto(mensaje, empleado, datos):
    """
    Registra un gasto contra el fondo de una categoría, siguiendo estos pasos:

    1) Intenta extraer categoría y monto directamente del mensaje original.
       Si falta alguno de los dos datos, lo pide explícitamente por input().
    2) Calcula cuánto quedaría disponible si se hiciera el gasto.
    3) Según el resultado, hay tres caminos posibles:
         - Caso 1: queda saldo positivo -> pide confirmación y, si el
           usuario confirma, descuenta el monto y guarda en el CSV.
         - Caso 2: el saldo quedaría exactamente en cero -> advierte
           que se queda sin fondos, pide confirmación y guarda igual.
         - Caso 3: el gasto supera el fondo disponible -> rechaza la
           operación directamente, sin pedir confirmación, e informa
           cuánto le faltaría para poder cubrirlo.
    """
    categoria = extraer_categoria(mensaje)
    monto = extraer_monto(mensaje)

    # Si no detectó categoría en el mensaje, se la pregunta directamente
    if categoria is None:
        categoria = input("🤖 ¿En qué categoría es el gasto?: ").lower()
        if extraer_categoria(categoria) is None:
            print("❌ Esa categoría no existe.")
            return
        categoria = extraer_categoria(categoria)

    # Si no detectó monto en el mensaje, se lo pregunta directamente
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
        print(f"💵 Si lo hacés, te van a quedar ${fondo_restante}.")
        
        confirmar = input("🤖 ¿Querés confirmar el gasto? (si/no): ").lower()

        if es_confirmacion(confirmar):
            # Actualiza el registro del empleado dentro de la lista completa,
            # buscando por legajo (clave única) en lugar de por posición,
            # para evitar tocar el registro de otro empleado por error.
            for emp in datos:
                if emp["legajo"] == empleado["legajo"]:
                    emp[categoria] = str(fondo_restante)
            guardar_datos(datos)
            empleado[categoria] = str(fondo_restante)  # mantiene sincronizado el objeto en memoria
            print("✔ Gasto registrado correctamente.")
        else:
            print("❌ Gasto cancelado.")

    # CASO 2 — Puede hacer el gasto pero queda en cero
    elif fondo_restante == 0:
        print(f"⚠ {empleado['nombre']}, podés hacer el gasto, pero te quedarías SIN fondos.")
        
        confirmar = input("🤖 ¿Querés confirmar el gasto? (si/no): ").lower()

        if es_confirmacion(confirmar):
            for emp in datos:
                if emp["legajo"] == empleado["legajo"]:
                    emp[categoria] = "0"
            guardar_datos(datos)
            empleado[categoria] = "0"
            print("✔ Gasto registrado. Te quedaste sin fondos.")
        else:
            print("❌ Gasto cancelado.")

    # CASO 3 — No puede hacer el gasto (el monto supera el fondo disponible)
    else:
        print(f"❌ {empleado['nombre']}, no podés hacer este gasto.")
        print(f"Te faltarían ${abs(fondo_restante)} para poder cubrirlo.")

# ============================================================
#   EJECUCIÓN DIRECTA DEL CHATBOT
# ============================================================

print("🤖 Hola! Soy el Chatbot de OE. Antes de empezar, necesito identificarte.")
print("Escribí 'salir' para terminar.")

datos = cargar_datos()
empleado = None

# IDENTIFICACIÓN
# Este bucle es el control de acceso: no se sale de él (ni se continúa
# con el resto del programa) hasta que se ingrese un legajo, DNI o
# nombre que exista en la base de datos, o hasta que el usuario escriba "salir".
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
# "esperando_categoria" funciona como una memoria de un solo paso: cuando
# el bot le preguntó al usuario por una categoría pendiente, esta bandera
# se pone en True para que el próximo mensaje se interprete directamente
# como la respuesta a esa pregunta, en lugar de pasar por detectar_intencion.
esperando_categoria = False

while True:
    mensaje = input(f"\n{nombre}: ")

    if mensaje.lower() == "salir":
        procesar_despedida(nombre)
        break

    # Si estamos esperando categoría, NO analizamos intención:
    # el mensaje actual se interpreta como la categoría pedida.
    if esperando_categoria:
        categoria = extraer_categoria(mensaje)

        if categoria is None:
            print("❌ Esa categoría no existe. Probá con viaticos, comida, transporte o insumos.")
        else:
            procesar_consulta_fondos(mensaje, empleado)
            esperando_categoria = False  # volvemos al modo normal
        continue

    # Detectar intención normalmente
    intencion = detectar_intencion(mensaje)

    if intencion == "saludo":
        procesar_saludo(nombre)

    elif intencion == "despedida":
        procesar_despedida(nombre)
        break

    elif intencion == "consultar_fondos":
        # Se le pide la categoría al usuario y se activa la bandera para
        # interpretar la próxima respuesta como esa categoría pendiente.
        print("🤖 ¿De qué categoría querés saber el fondo? (viaticos, comida, transporte, insumos)")
        esperando_categoria = True

    elif intencion == "cargar_gasto":
        procesar_carga_gasto(mensaje, empleado, datos)

    else:
        print(f"🤖 No entendí lo que quisiste decir, {nombre}. Podés decir cosas como:")
        print("   - 'quiero cargar un gasto'")
        print("   - 'cuánto me queda en viáticos'")
        print("   - 'tengo un gasto de 500 en comida'")
        print("   - 'quiero ver mis fondos'")
