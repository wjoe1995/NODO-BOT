import os
import telebot
from dotenv import load_dotenv
import requests
from telebot import types
from servicios.obtenerEstudiante import obtener_id_estudiante

load_dotenv()

BOT_TOKEN = os.environ.get('TELEGRAM_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

def mostrar_solicitud_tutoria(message):
    try:
        id_telegram = message.chat.id
        estudiante_id = obtener_id_estudiante(id_telegram)
        url = f'https://localhost:8080/api/solicitud_tutoria/obtenerSolicitudTutoriaEstu/{estudiante_id}'
        bot.reply_to(message, "Estas son las solicitudes registradas:")
        response = requests.get(url, verify=False)
        solicitudes = response.json()
        
        if len(solicitudes) == 0:
            bot.reply_to(message, "No se encontraron solicitudes registradas.")
        else:
            for i, solicitud in enumerate(solicitudes, start=1):
                estudiante_nombre = solicitud['estudiante']['nombre']
                tutor_nombre = solicitud['tutor']['nombre'] if solicitud['tutor'] else "No asignado"
                clase_nombre = solicitud['clase']['nombre_clase']
                horario_solicitado = f"{solicitud['horario_solicitado']['dia']} de {solicitud['horario_solicitado']['hora']}"
                estado_dict = {"0": "PENDIENTE", "1": "APROBADA", "2": "NO APROBADA"}
                estado = estado_dict[solicitud['estado']]
                solicitud_info = f"{i}. Estudiante: {estudiante_nombre}\nTutor: {tutor_nombre}\nClase: {clase_nombre}\nHorario solicitado: {horario_solicitado}\nEstado: {estado}\n\n"
                bot.send_message(message.chat.id, solicitud_info)
    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al buscar las solicitudes.")

def eliminar_solicitud_tutoria(bot, message):
    try:
        id_telegram = message.chat.id
        estudiante_id = obtener_id_estudiante(id_telegram)
        url = f'https://localhost:8080/api/solicitud_tutoria/obtenerSolicitudTutoriaEstu/{estudiante_id}'
        bot.reply_to(message, "Estas son las solicitudes registradas:")
        response = requests.get(url, verify=False)
        solicitudes = response.json()
        
        if len(solicitudes) == 0:
            bot.reply_to(message, "No se encontraron solicitudes registradas.")
        else:
            for i, solicitud in enumerate(solicitudes, start=1):
                estudiante_nombre = solicitud['estudiante']['nombre']
                tutor_nombre = solicitud['tutor']['nombre'] if solicitud['tutor'] else "No asignado"
                clase_nombre = solicitud['clase']['nombre_clase']
                horario_solicitado = f"{solicitud['horario_solicitado']['dia']} de {solicitud['horario_solicitado']['hora']}"
                estado_dict = {"0": "PENDIENTE", "1": "APROBADA", "2": "NO APROBADA"}
                estado = estado_dict[solicitud['estado']]
                solicitud_info = f"{i}. Estudiante: {estudiante_nombre}\nTutor: {tutor_nombre}\nClase: {clase_nombre}\nHorario solicitado: {horario_solicitado}\nEstado: {estado}\n\n"
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

            url = f'https://localhost:8080/api/solicitud_tutoria/eliminarSolicitudTutoria/{solicitud_id}'
            response = requests.delete(url, verify=False)

            if response.status_code == 200:
                bot.reply_to(message, "¡Gracias por eliminar la solicitud! Pronto nos pondremos en contacto contigo.")
            else:
                bot.reply_to(message, "Ocurrió un error al eliminar la solicitud. Por favor, intenta de nuevo.")
    
    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")


def solicitar_tutoria(message):
    try:
        # First, greet the user
        bot.reply_to(message, "Para crear una solicitud, ingresa los siguientes datos:")

        # Get the list of available classes
        url = 'https://localhost:8080/api/clases/'
        response = requests.get(url, verify=False)
        clases = response.json()

        # Display the list of classes to the user
        bot.reply_to(message, "Estas son las clases disponibles:")
        for i, clase in enumerate(clases, start=1):
            id_clase  = clase['_id']
            nombre_clase = clase['nombre_clase']
            codigo_clase = clase['codigo_clase']
            carrera = ', '.join(carrera for carrera in clase['carrera'])
            bot.send_message(message.chat.id, f"{i}. Código de clase: {codigo_clase}\nNombre de la clase: {nombre_clase}\nCarrera(s): {carrera}")

        bot.register_next_step_handler(message, handle_clasetu_selection, clases)
    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")
    
    bot.reply_to(message, "Por favor, ingresa una clase atravez de su enumeración:(Por ejemplo 1)")

def handle_clasetu_selection(message, clases):
    try:
        reply = message.text.strip()
        i = int(reply)
        if i < 1 or i > len(clases):
            bot.reply_to(message, f"Por favor, ingresa un número entre 1 y {len(clases)}.")
            bot.register_next_step_handler(message, handle_clasetu_selection, clases)
        else:
            clase_id = clases[i-1]['_id']

            # Get the list of available tutors
            url = f'https://localhost:8080/api/solicitud_tutor/obtenerSolicitudTutorClase/{clase_id}'
            response = requests.get(url, verify=False)
            tutores = response.json()
            text = message.text

        # Verificar si el usuario quiere cancelar el proceso actual
            if text.lower() == '/cancelar':
        # Enviar mensaje de confirmación de cancelación
                bot.send_message(chat_id, "Proceso actual cancelado. ¡Gracias por usar nuestro servicio! Si necesitas algo más, no dudes en escribirnos de nuevo.")
                return
            if not tutores:
                chat_id = message.chat.id
                # Si no hay tutores disponibles, ofrecer la opción de cancelar
                message_text = "Lo siento, actualmente no hay tutores disponibles para esa clase. ¿Te gustaría cancelar el proceso actual y volver al menú principal? Si es así, envía /menu."
                bot.send_message(chat_id, message_text)
                return
            else:
            # Display the list of tutors to the user
                bot.reply_to(message, "Estos son los tutores disponibles para la clase seleccionada:")
                for i, tutor in enumerate(tutores, start=1):
                    nombre = tutor['estudiante']['nombre']
                    horarios = tutor['horario_solicitado']['dia'] + " " + tutor['horario_solicitado']['hora']  
                    bot.send_message(message.chat.id, f"{i}. Nombre: {nombre}\nHorarios de tutorías: {horarios}")

            bot.register_next_step_handler(message, handle_tutor_selection, clase_id, tutores)

    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un número válido.")
        bot.register_next_step_handler(message, handle_clasetu_selection, clases)


def handle_tutor_selection(message, clase_id, tutores):
    try:
        reply = message.text.strip()
        i = int(reply)
        if i < 1 or i > len(tutores):
            bot.reply_to(message, f"Por favor, ingresa un número entre 1 al {len(tutores)}.")
            bot.register_next_step_handler(message, handle_tutor_selection, clase_id, tutores)
        else:
            tutor_id = tutores[i-1]['_id']
            tutor_horario = tutores[i-1]['horario_solicitado']

            # Create the tutorship request
            url = ' https://localhost:8080/api/solicitud_tutoria/crearSolicitudTutoria'
            data = {
                'estudiante': '643b1767abf8200459d70aff',
                'clase': clase_id,
                'tutor': tutor_id,
                'horario_solicitado': tutor_horario
            }
            response = requests.post(url, json=data, verify=False)

            if response.status_code == 200:
                bot.reply_to(message, "¡Gracias por crear la solicitud! Pronto nos pondremos en contacto contigo.")
            else:
                bot.reply_to(message, "Ocurrió un error al crear la solicitud. Por favor, intenta de nuevo.")

    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un número válido.")
        bot.register_next_step_handler(message, handle_tutor_selection, clase_id, tutores)