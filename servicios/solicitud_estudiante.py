import os
import telebot
from dotenv import load_dotenv
import requests
from telebot import types
import subprocess
import re

load_dotenv()

#1271515359
BOT_TOKEN = os.environ.get('TELEGRAM_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

def crear_solicitud_estudiante(bot,message):
    try:
        # Inicializar el objeto de solicitud de tutoría
        solicitud = {"estudiante": {}}

        # Pedir al usuario el número de cuenta
        bot.reply_to(message, "Por favor ingrese el número de cuenta del estudiante.")
        bot.register_next_step_handler(message, lambda respuesta: obtener_nombre(respuesta, solicitud))

    except Exception as e:
        bot.reply_to(message, f"Ocurrió un error al crear la solicitud de estudiante: {str(e)}")
def obtener_nombre(message, solicitud):
    # Verificar que el número de cuenta tenga el formato correcto
    if not re.match(r'^\d{11}$', message.text):
        bot.reply_to(message, "Por favor ingrese un número de cuenta válido.")
        return
    # Guardar el número de cuenta en la solicitud
    solicitud["estudiante"]["numero_cuenta"] = message.text

    # Pedir al usuario el nombre completo
    bot.reply_to(message, "Por favor ingrese el nombre completo del estudiante.")

    # Registrar el siguiente paso de la conversación con una función lambda separada
    bot.register_next_step_handler(message, lambda respuesta: obtener_nombre_ca(respuesta, solicitud))
def obtener_nombre_ca(message, solicitud):
    # Guardar el nombre completo en la solicitud
    solicitud["estudiante"]["nombre"] = message.text

    # Pedir al usuario la carrera
    bot.reply_to(message, "Por favor confirma tu nombre:")

    # Registrar el siguiente paso de la conversación con una función lambda separada
    bot.register_next_step_handler(message, lambda respuesta: obtener_carrera(respuesta, solicitud))
def obtener_carrera(message, solicitud):
    # Realizar una petición GET a la API para obtener la lista de carreras
    url = "https://localhost:8080/api/carreras/obtenerCarreras"
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        bot.reply_to(message, "Ocurrió un error al obtener la lista de carreras.")
        return

    # Guardar la lista de carreras en una variable
    carreras = response.json()

    # Crear un mensaje con la lista numerada de opciones
    mensaje = "Por favor seleccione la carrera del estudiante:\n"
    for i, carrera in enumerate(carreras):
        mensaje += f"{i + 1}. {carrera['nombre_carrera']}\n"
    bot.reply_to(message, mensaje)

    # Pedir al usuario que ingrese el número de la carrera que desea seleccionar
    bot.register_next_step_handler(message, lambda respuesta: obtener_telefono(respuesta, solicitud, carreras))
def obtener_telefono(message, solicitud, carreras):
    # Obtener la carrera seleccionada y guardar su ID en la solicitud
    try:
        numero_carrera = int(message.text)
        if numero_carrera < 1 or numero_carrera > len(carreras):
            raise ValueError()
        solicitud["estudiante"]["carrera"] = carreras[numero_carrera - 1]["_id"]
    except ValueError:
        bot.reply_to(message, "Por favor ingrese un número válido.")
        bot.register_next_step_handler(message, lambda respuesta: obtener_telefono(respuesta, solicitud, carreras))
        return

    # Pedir al usuario el teléfono (opcional)
    bot.reply_to(message, "Por favor ingrese el número de teléfono del estudiante (opcional).")
    bot.register_next_step_handler(message, lambda respuesta: obtener_id_telegram(respuesta, solicitud))
def obtener_id_telegram(message, solicitud):
    # Guardar el teléfono en la solicitud (si se proporciona)
    if message.text:
        solicitud["estudiante"]["telefono"] = message.text

    # Guardar el ID de Telegram en la solicitud
    solicitud["estudiante"]["id_telegram"] = message.chat.id

    # Enviar la solicitud a la API
    enviar_solicitud(message, solicitud)
def enviar_solicitud(message, solicitud):
    # Guardar el ID de Telegram en la solicitud (si se proporciona)
    if message.text:
        solicitud["estudiante"]["id_telegram"] = message.chat.id

    # Enviar la solicitud a la API
    url = "https://localhost:8080/api/estudiantes/crearEstudiante"
    data = {
        "numero_cuenta": solicitud["estudiante"]["numero_cuenta"],
        "nombre": solicitud["estudiante"]["nombre"],
        "carrera": solicitud["estudiante"]["carrera"],
        "telefono": solicitud["estudiante"].get("telefono", ""),
        "id_telegram": solicitud["estudiante"].get("id_telegram", "")
    }
    response = requests.post(url, json=data,  verify=False)

    # Comprobar si se creó la solicitud correctamente
    if response.status_code == 200:
        bot.reply_to(message, "La solicitud de estudiante se creó correctamente.")
    elif response.status_code == 409:
        bot.reply_to(message, "El estudiante ya existe.")
    else:
        bot.reply_to(message, "Ocurrió un error al crear la solicitud de estudiante.")
