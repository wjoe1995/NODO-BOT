import os
import telebot
from dotenv import load_dotenv
import requests
from telebot import types
import subprocess
from servicios.solicitud_tutoria import mostrar_solicitud_tutoria, solicitar_tutoria, eliminar_solicitud_tutoria
from servicios.solicitud_tutor import  mostrar_solicitud_tutor , crear_solicitud_tutor, eliminar_solicitud_tutor
from servicios.usuario import usuarios

load_dotenv()

#1271515359
BOT_TOKEN = os.environ.get('TELEGRAM_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

def menu_interactivo(chat_id, opciones):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for opcion in opciones:
        keyboard.add(opcion)
    bot.send_message(chat_id, "Seleccione una opción:", reply_markup=keyboard)

@bot.message_handler(commands=['menu'])
def menu(message):
    opciones = {
        #"start": "/start",
        #"aulas": "/aulas",
        #"usuarios": "/usuarios",
        "Solicitud de Registro de Estudiantes": "/solicitudRegistroEstudiantes",
        "Tutorias": {
            "Ver tutorias disponibles": "/verTutoriasDisponibles",
            "Ver tutorias activas": "/verTutoriasActivas",
            "Ver mi historial de tutorias recibidas": "/verHistorialTutoriasRecibidas",
            "Regresar": "back"
        },
        "Solicitar tutoria": {
                "Formulario de solicitud": "/solicitarTutoria",
                "Ver estado de solicitud": "/miSolicitudTutoria",
                "Eliminar solicitud": "/eliminarSolicitudTutoria",
                "Regresar": "back"
            },
        "Solicitar ser tutor": {
                "Formulario de solicitud": "/solicitudSerTutor",
                "Ver estado de solicitud": "/miSolicitudTutor",
                "Eliminar solicitud": "/eliminarSolicitudTutor",
                "Regresar": "back"
            },
        "Opciones de tutor": {
            "Ver tutorias activas": "/verTutoriasActivas",
            "Ver mi historial de tutorias impartidas": "/verHistorialTutoriasImpartidas",
            "Regresar": "back"
            }, 
    }
    menu_interactivo(message.chat.id, opciones.keys())
    bot.register_next_step_handler(message, lambda m: seleccionar_opcion(m, opciones))

  

    def seleccionar_opcion(message, opciones, historial=[]):
        opcion_seleccionada = message.text
        if opcion_seleccionada in opciones:
            comando = opciones[opcion_seleccionada]
            if isinstance(comando, dict):  # Si la opción seleccionada es un diccionario, mostrar un submenú
                historial.append(opciones)  # Agregar el menú actual al historial
                menu_interactivo(message.chat.id, comando.keys())
                bot.register_next_step_handler(message, lambda m: seleccionar_opcion(m, comando, historial))
            elif comando == "back":  # Si la opción seleccionada es "Atrás", retroceder en el historial
                if historial:
                    menu_anterior = historial.pop()
                    menu_interactivo(message.chat.id, menu_anterior.keys())
                    bot.register_next_step_handler(message, lambda m: seleccionar_opcion(m, menu_anterior, historial))
                else:
                    bot.send_message(message.chat.id, "No hay menú anterior")
            else:
                mensaje_comando = f"Ejecuta el comando {comando}"
                bot.send_message(message.chat.id, mensaje_comando)
                try:
                    bot.send_message(message.chat.id, comando)
                except Exception as e:
                    bot.send_message(message.chat.id, f"Error al ejecutar el comando: {str(e)}")
        else:
            bot.send_message(message.chat.id, "Opción inválida")



@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hola, soy un bot de Telegram. ¿En qué te puedo ayudar?")


@bot.message_handler(commands=['aulas'])
def aulas(message):
    try:
        url = 'https://localhost:8080/api/aulas/'
        bot.reply_to(message, "Aulas disponibles:")
        response = requests.get(url, verify=False)
        data = response.json()
        for i, aula in enumerate(data, start=1):
            numero = aula["numero"]
            bot.send_message(message.chat.id, f"{i}. Aula #{numero}")
    except Exception as e:
        bot.reply_to(message, "Error al obtener las aulas")

@bot.message_handler(commands=['usuarios'])
def usuarios_command(message):
# Invocar la función de solicitud de tutoría
    usuarios(message)


@bot.message_handler(commands=['solicitudSerTutor'])
def crear_solicitud_tutor(message):
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

        bot.register_next_step_handler(message, handle_clase_selection, clases)

    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")
    
    bot.reply_to(message, "Por favor, ingresa una clase atravez de su enumeración:(Por ejemplo 1)")
def handle_clase_selection(message, clases):
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
            response = requests.get(urlHo, verify=False)
            horarios = response.json()
            # Display the list of schedules to the user
            bot.reply_to(message, "Estos son los horarios disponibles:")
            for i, horario in enumerate(horarios, start=1):
                id_horario = horario['_id']
                dia = horario['dia']
                hora = horario['hora']
                bot.send_message(message.chat.id, f"{i}. Día: {dia}\nHora: {hora}")
            bot.register_next_step_handler(message, handle_horario_selection, clase_id, horarios)
            bot.reply_to(message, "Gracias ahora por favor, ingresa un horario a través de su enumeración: (Por ejemplo 1)")

    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un número válido.")
        bot.register_next_step_handler(message, handle_clase_selection, clases)
def handle_horario_selection(message, clase_id, horarios):
    try:
        reply = message.text.strip()
        i = int(reply)
        if i < 1 or i > len(horarios):
            bot.reply_to(message, f"Por favor, ingresa un número entre 1 al {len(horarios)}.")
            bot.register_next_step_handler(message, handle_horario_selection, clase_id, horarios)
        else:
            horario_id = horarios[i-1]['_id']
            bot.reply_to(message, "Horario seleccionado.")

    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un número válido.")
        bot.register_next_step_handler(message, handle_horario_selection, clase_id, horarios)


        # Create the tutor request
    url = 'https://localhost:8080/api/solicitud_tutor/crearSolicitudTutor'
    data = {
        'estudiante': '6448125e30da409bf7eca39b',
        'clase': clase_id,
        'horario_solicitado': horario_id
    }
    response = requests.post(url, json=data, verify=False)

    if response.status_code == 200:
        bot.reply_to(message, "¡Gracias por crear la solicitud! Pronto nos pondremos en contacto contigo.")
    else:
        bot.reply_to(message, "Ocurrió un error al crear la solicitud. Por favor, intenta de nuevo.")


@bot.message_handler(commands=['solicitarTutoria'])
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
            tutor_id = tutores[i-1]['estudiante']
            tutor_horario = tutores[i-1]['horario_solicitado']

            # Create the tutorship request
            url = ' https://localhost:8080/api/solicitud_tutoria/crearSolicitudTutoria'
            data = {
                'estudiante': '6448118730da409bf7eca39a',
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

@bot.message_handler(commands=['miSolicitudTutor'])
def mostrar_solicitud_tutor_command(message):
# Invocar la función de solicitud de tutor
    mostrar_solicitud_tutor(message)

@bot.message_handler(commands=['miSolicitudTutoria'])
def mostrar_solicitud_tutoria_command(message):
# Invocar la función de solicitud de tutoría
    mostrar_solicitud_tutoria(message)


@bot.message_handler(commands=['eliminarSolicitudTutoria'])
def mostrar_solicitud_tutoria_command(message):
# Invocar la función de solicitud de tutoría
    eliminar_solicitud_tutoria(bot, message)

@bot.message_handler(commands=['eliminarSolicitudTutor'])
def mostrar_solicitud_tutor_command(message):
# Invocar la función de solicitud de tutoría
    eliminar_solicitud_tutor(bot, message)

@bot.message_handler(commands=['clases'])
def obtener_clases(message):
    try:
        url = 'https://localhost:8080/api/clases/'
        bot.reply_to(message, "Clases registradas:")
        response = requests.get(url, verify=False)
        data = response.json()
        clases_dict = {}
        for i, clase in enumerate(data, start=1):
            id_clase  = clase['_id']
            nombre_clase = clase['nombre_clase']
            codigo_clase = clase['codigo_clase']
            carrera = ', '.join(carrera for carrera in clase['carrera'])
            clases_dict[codigo_clase] = {'nombre_clase': nombre_clase, 'carrera': carrera}
        for codigo_clase, clase_data in clases_dict.items():
            bot.send_message(message.chat.id, f"{i}. Código de clase: {codigo_clase}\nNombre de la clase: {clase_data['nombre_clase']}\nCarrera(s): {clase_data['carrera']}")
    except Exception as e:
        bot.reply_to(message, "Error al obtener las clases" + str(e))


bot.add_message_handler(start)
bot.add_message_handler(aulas)
bot.add_message_handler(usuarios)
bot.add_message_handler(crear_solicitud_tutor)
bot.add_message_handler(solicitar_tutoria)
bot.add_message_handler(mostrar_solicitud_tutor)
bot.add_message_handler(mostrar_solicitud_tutoria)
bot.add_message_handler(eliminar_solicitud_tutoria)
bot.add_message_handler(eliminar_solicitud_tutor)
bot.add_message_handler(menu)


bot.infinity_polling()

