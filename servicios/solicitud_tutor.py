import os
import telebot
from dotenv import load_dotenv
import requests
from telebot import types
from servicios.obtenerEstudiante import obtener_id_estudiante

load_dotenv()

#1271515359
BOT_TOKEN = os.environ.get('TELEGRAM_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

def mostrar_solicitud_tutor(message,token):
    try:
        id_telegram = message.chat.id
        estudiante_id = obtener_id_estudiante(id_telegram)
        url = f'https://localhost:8080/api/solicitud_tutor/obtenerSolicitudTutorEstudiante/{estudiante_id}'
        headers = {
            'Authorization': 'Bearer ' + token
        }
       # Agregar el token JWT al encabezado de autorización
        response = requests.get(url, headers=headers, verify=False)
        bot.reply_to(message, "Estas son las solicitudes registradas:")
        solicitudes = response.json()
        if len(solicitudes) == 0:
            bot.reply_to(message, "No se encontraron solicitudes registradas.")
        else:
            for i, solicitud in enumerate(solicitudes, start=1):
                estudiante_nombre = solicitud['estudiante']['nombre']
                clase_nombre = solicitud['clase']['nombre_clase']
                horario_solicitado = f"{solicitud['horario_solicitado']['dia']} de {solicitud['horario_solicitado']['hora']}"
                estado_dict = {"0": "PENDIENTE", "1": "APROBADA", "2": "NO APROBADA"}
                estado = estado_dict[solicitud['estado']]
                solicitud_info = f"{i}. Estudiante: {estudiante_nombre}\nClase: {clase_nombre}\nHorario solicitado: {horario_solicitado}\nEstado: {estado}\n\n"
                bot.send_message(message.chat.id, solicitud_info)
    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al buscar las solicitudes.")

    
def eliminar_solicitud_tutor(bot, message, token):
    try:
        id_telegram = message.chat.id
        estudiante_id = obtener_id_estudiante(id_telegram)
        url = f'https://localhost:8080/api/solicitud_tutor/obtenerSolicitudTutorEstudiante/{estudiante_id}'
        headers = {
            'Authorization': 'Bearer ' + token
        }
       # Agregar el token JWT al encabezado de autorización
        response = requests.get(url, headers=headers, verify=False)
        bot.reply_to(message, "Estas son las solicitudes registradas:")
        solicitudes = response.json()
        if len(solicitudes) == 0:
            bot.reply_to(message, "No se encontraron solicitudes registradas.")
        else:
            for i, solicitud in enumerate(solicitudes, start=1):
                estudiante_nombre = solicitud['estudiante']['nombre']
                clase_nombre = solicitud['clase']['nombre_clase']
                horario_solicitado = f"{solicitud['horario_solicitado']['dia']} de {solicitud['horario_solicitado']['hora']}"
                estado_dict = {"0": "PENDIENTE", "1": "APROBADA", "2": "NO APROBADA"}
                estado = estado_dict[solicitud['estado']]
                solicitud_info = f"{i}. Estudiante: {estudiante_nombre}\nClase: {clase_nombre}\nHorario solicitado: {horario_solicitado}\nEstado: {estado}\n\n"
                bot.send_message(message.chat.id, solicitud_info)
            
            bot.register_next_step_handler(message, handle_solicitudtu_selection, solicitudes, token)

    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")
def handle_solicitudtu_selection(message, solicitudes, token):
    try:
        reply = message.text.strip()
        i = int(reply)
        if i < 1 or i > len(solicitudes):
            bot.reply_to(message, f"Por favor, ingresa un número entre 1 y {len(solicitudes)}.")
            bot.register_next_step_handler(message, handle_solicitudtu_selection, solicitudes)
        else:
            solicitud_id = solicitudes[i-1]['_id']

            url = f'https://localhost:8080/api/solicitud_tutor/eliminarSolicitudTutor/{solicitud_id}'

            headers = {
            'Authorization': 'Bearer ' + token
                }
      
            response = requests.delete(url, headers=headers,verify=False)

            if response.status_code == 200:
                bot.reply_to(message, "¡Gracias por eliminar la solicitud! Pronto nos pondremos en contacto contigo.")
            else:
                bot.reply_to(message, "Ocurrió un error al eliminar la solicitud. Por favor, intenta de nuevo.")
    
    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")


def crear_solicitud_tutor(message,token):
    try:
        # First, greet the user
        bot.reply_to(message, "Para crear una solicitud, ingresa los siguientes datos:")

        # Get the list of available classes
        url = 'https://localhost:8080/api/clases/'
        headers = {
            'Authorization': 'Bearer ' + token
        }
        response = requests.get(url, headers=headers, verify=False)
        clases = response.json()

        # Display the list of classes to the user
        bot.reply_to(message, "Estas son las clases disponibles:")
        for i, clase in enumerate(clases, start=1):
            id_clase  = clase['_id']
            nombre_clase = clase['nombre_clase']
            codigo_clase = clase['codigo_clase']
            bot.send_message(message.chat.id, f"{i}. Código de clase: {codigo_clase}\nNombre de la clase: {nombre_clase}")

        bot.register_next_step_handler(message, handle_clase_selection, clases, token)

    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")
    
    bot.reply_to(message, "Por favor, ingresa una clase atravez de su enumeración:(Por ejemplo 1)")
def handle_clase_selection(message, clases, token):
    try:
        reply = message.text.strip()
        i = int(reply)
        if i < 1 or i > len(clases):
            bot.reply_to(message, f"Por favor, ingresa un número entre 1 y {len(clases)}.")
            bot.register_next_step_handler(message, handle_clase_selection, clases)
        else:
            clase_id = clases[i-1]['_id']

            # Get the list of available schedules
            urlHo = 'https://localhost:8080/api/horario/obtenerHorarios'
            headers = {
            'Authorization': 'Bearer ' + token
            }
            response = requests.get(urlHo,headers=headers, verify=False)
            horarios = response.json()
            # Display the list of schedules to the user
            bot.reply_to(message, "Estos son los horarios disponibles:")
            for i, horario in enumerate(horarios, start=1):
                id_horario = horario['_id']
                dia = horario['dia']
                hora = horario['hora']
                bot.send_message(message.chat.id, f"{i}. Día: {dia}\nHora: {hora}")
            bot.register_next_step_handler(message, handle_horario_selection, clase_id, horarios, token)
            bot.reply_to(message, "Gracias ahora por favor, ingresa un horario a través de su enumeración: (Por ejemplo 1)")

    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un número válido.")
        bot.register_next_step_handler(message, handle_clase_selection, clases, token)
def handle_horario_selection(message, clase_id, horarios,token):
    try:
        reply = message.text.strip()
        i = int(reply)
        if i < 1 or i > len(horarios):
            bot.reply_to(message, f"Por favor, ingresa un número entre 1 al {len(horarios)}.")
            bot.register_next_step_handler(message, handle_horario_selection, clase_id, horarios,token)
        else:
            horario_id = horarios[i-1]['_id']
            bot.reply_to(message, "Horario seleccionado.")

    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un número válido.")
        bot.register_next_step_handler(message, handle_horario_selection, clase_id, horarios,token)
    
    id_telegram = message.chat.id
    estudiante_id = obtener_id_estudiante(id_telegram)
        # Create the tutor request
    url = 'https://localhost:8080/api/solicitud_tutor/crearSolicitudTutor'
    headers = {
            'Authorization': 'Bearer ' + token
            }
    data = {
        'estudiante': estudiante_id,
        'clase': clase_id,
        'horario_solicitado': horario_id
    }
    response = requests.post(url, json=data,headers=headers, verify=False)

    if response.status_code == 200:
        bot.reply_to(message, "¡Gracias por crear la solicitud! Pronto nos pondremos en contacto contigo.")
    else:
        bot.reply_to(message, "Ocurrió un error al crear la solicitud. Por favor, intenta de nuevo.")
