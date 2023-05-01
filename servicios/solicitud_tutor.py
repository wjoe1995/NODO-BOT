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

def mostrar_solicitud_tutor(message):
    try:
        id_telegram = message.chat.id
        estudiante_id = obtener_id_estudiante(id_telegram)
        url = f'https://localhost:8080/api/solicitud_tutor/obtenerSolicitudTutorEstudiante/{estudiante_id}'

       # Agregar el token JWT al encabezado de autorización
        response = requests.get(url, verify=False)
        bot.reply_to(message, "Estas son las solicitudes registradas:")
        solicitudes = response.json()
        if len(solicitudes) == 0:
            bot.reply_to(message, "No se encontraron solicitudes registradas.")
        else:
            for i, solicitud in enumerate(solicitudes, start=1):
                estudiante_nombre = solicitud['estudiante']['nombre']
                clase_nombre = solicitud['clase']['nombre_clase']
                nombre = solicitud['estudiante']['nombre']
                horarios_disponibles = "\n ".join(f"{horario['dia']} {horario['hora']}" for horario in solicitud['horario_solicitado'])
                estado_dict = {"0": "PENDIENTE", "1": "APROBADA", "2": "NO APROBADA"}
                estado = estado_dict[solicitud['estado']]
                solicitud_info = f"{i}. Estudiante: {estudiante_nombre}\nClase: {clase_nombre}\nHorario solicitado: {horarios_disponibles}\nEstado: {estado}\n\n"
                bot.send_message(message.chat.id, solicitud_info)
    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al buscar las solicitudes.")

    
def eliminar_solicitud_tutor(bot, message):
    try:
        id_telegram = message.chat.id
        estudiante_id = obtener_id_estudiante(id_telegram)
        url = f'https://localhost:8080/api/solicitud_tutor/obtenerSolicitudTutorEstudiante/{estudiante_id}'

       # Agregar el token JWT al encabezado de autorización
        response = requests.get(url,  verify=False)
        bot.reply_to(message, "Estas son las solicitudes registradas:")
        solicitudes = response.json()
        if len(solicitudes) == 0:
            bot.reply_to(message, "No se encontraron solicitudes registradas.")
        else:
            for i, solicitud in enumerate(solicitudes, start=1):
                estudiante_nombre = solicitud['estudiante']['nombre']
                clase_nombre = solicitud['clase']['nombre_clase']
                horarios_disponibles = "\n ".join(f"{horario['dia']} {horario['hora']}" for horario in solicitud['horario_solicitado'])                
                estado_dict = {"0": "PENDIENTE", "1": "APROBADA", "2": "NO APROBADA"}
                estado = estado_dict[solicitud['estado']]
                solicitud_info = f"{i}. Estudiante: {estudiante_nombre}\nClase: {clase_nombre}\nHorario solicitado: {horarios_disponibles}\nEstado: {estado}\n\n"
                bot.send_message(message.chat.id, solicitud_info)
            
            bot.register_next_step_handler(message, handle_solicitudtu_selection, solicitudes)

    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")
def handle_solicitudtu_selection(message, solicitudes):
    try:
        reply = message.text.strip()
        i = int(reply)
        if i < 1 or i > len(solicitudes):
            bot.reply_to(message, f"Por favor, ingresa un número entre 1 y {len(solicitudes)}.")
            bot.register_next_step_handler(message, handle_solicitudtu_selection, solicitudes)
        else:
            solicitud_id = solicitudes[i-1]['_id']

            url = f'https://localhost:8080/api/solicitud_tutor/eliminarSolicitudTutor/{solicitud_id}'

      
            response = requests.delete(url, verify=False)

            if response.status_code == 200:
                bot.reply_to(message, "¡Solicitud Eliminada Exitosamente!.")
            else:
                bot.reply_to(message, "Ocurrió un error al eliminar la solicitud. Por favor, intenta de nuevo.")
    
    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")

