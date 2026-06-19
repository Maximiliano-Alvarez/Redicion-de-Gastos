# Redicion-de-Gastos

Chatbot para OE
📌 Descripción del proyecto
Chatbot para OE es un sistema conversacional en Python que permite a los empleados registrar gastos, validar categorías, controlar fondos disponibles y actualizar la información en un archivo CSV que actúa como base de datos.
El objetivo es automatizar la carga de gastos y asegurar que cada empleado respete los fondos asignados a cada categoría.

🎯 Funcionalidades principales
✔ Identificación del empleado
El chatbot permite identificar al trabajador mediante:

Legajo

Nombre y apellido

DNI

La identificación se valida contra la base de datos CSV.

✔ Registro de gastos
El empleado puede cargar un gasto indicando:

Categoría del gasto

Monto del gasto

Ambos datos son validados antes de continuar.

✔ Validación de categorías
Categorías disponibles:

viaticos

comida

transporte

insumos

✔ Validación del monto
El chatbot verifica que:

El monto sea numérico

Sea mayor a 0

✔ Control de fondos
Cada empleado tiene fondos asignados por categoría.
El chatbot determina si:

Hay fondos suficientes → gasto aprobado

No hay fondos suficientes → gasto rechazado

✔ Actualización del CSV
Si el gasto es aprobado:

Se descuenta el monto de la categoría correspondiente

Se actualiza el archivo CSV

Se muestra el fondo restante

📁 Estructura del archivo CSV
Archivo: empleados.csv

Código
legajo,nombre,dni,viaticos,comida,transporte,insumos
101,Juan Perez,30111222,20000,8000,5000,3000
102,Ana Lopez,28999111,15000,6000,4000,2000
103,Carlos Gomez,31222333,18000,7000,4500,2500
Columnas:

legajo, nombre, dni: identificación del empleado

viaticos, comida, transporte, insumos: fondos disponibles por categoría

🧠 Flujo del chatbot
El usuario inicia la conversación

El chatbot solicita identificación

Valida al empleado

Solicita categoría del gasto

Valida categoría

Solicita monto

Valida monto

Verifica fondos

Aprueba o rechaza

Si aprueba → actualiza CSV

Muestra el fondo restante

🛠️ Tecnologías utilizadas
Python 3.x

Módulo csv

Estructura modular basada en funciones

📦 Estructura del proyecto
Código
chatbot-para-OE/
│
├──files/(agregado de imagenes y pdfs)
├── empleados.csv
├── chatbot.py
└── README.md
🚀 Cómo ejecutar el proyecto
Clonar el repositorio

Verificar que Python 3 esté instalado

Ejecutar:

Código
python chatbot.py
Seguir las instrucciones del chatbot

📌 Estado del proyecto
🟢 En desarrollo
Próximas mejoras:

Historial de gastos

Reportes automáticos

Interfaz gráfica

Integración con base de datos SQL

👤 Autor
Maximiliano Álvarez  
Zulema Rodriguez
Proyecto académico — UTN
