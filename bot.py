import os
import telebot
from dotenv import load_dotenv
import requests
from telebot import types
import base64
from servicios.solicitud_tutoria import mostrar_solicitud_tutoria,  eliminar_solicitud_tutoria
from servicios.solicitud_tutor import  mostrar_solicitud_tutor , eliminar_solicitud_tutor
from servicios.tutorias import obtenerTutoriasEstudianteTutor, obtenerTutoriasEstudianteEstudiante
from servicios.obtenerEstudiante import obtener_id_estudiante
#from servicios.solicitud_estudiante import crear_solicitud_estudiante
import re

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
    # Comprobar si el estudiante ya ha sido aprobado
    url = f'https://localhost:8080/api/estudiantes/extraer/{message.chat.id}'
    response = requests.get(url, verify=False)

    if response.status_code != 200:
        bot.reply_to(message, "REGISTRATE  haciendo click en: /solicitudEstudiante")
        return
    estudiante = response.json()

    # Verificar si el estudiante ha sido aprobado
    if estudiante["activo"] == 1:
        opciones = {
            #"start": "/start",
            #"aulas": "/aulas",
            #"usuarios": "/usuarios",
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
    else:
        bot.reply_to(message, "Comunicate con el administrador para que aprueb tu solicitud")

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

@bot.message_handler(commands=['solicitarTutoria'])
def solicitar_tutoria_command(message):
    solicitar_tutoria(message)

@bot.message_handler(commands=['solicitudSerTutor'])
def solicitar_tutor_command(message):
    crear_solicitud_tutor(message)


@bot.message_handler(commands=['miSolicitudTutor'])
def mostrar_solicitud_tutor_command(message):
    mostrar_solicitud_tutor(message)

@bot.message_handler(commands=['miSolicitudTutoria'])
def mostrar_solicitud_tutoria_command(message):
    mostrar_solicitud_tutoria(message)

@bot.message_handler(commands=['solicitudEstudiante']) 
def mostrar_solicitud_tutoria_command(message):
    url = f'https://localhost:8080/api/estudiantes/extraer/{message.chat.id}'
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        crear_solicitud_estudiante(message)
    else:
        bot.reply_to(message, "Ya hicistes la solicitud. Por favor, comunicate con VOAE, para que aprueben tu solicitud.")

@bot.message_handler(commands=['eliminarSolicitudTutoria'])
def eliminar_solicitud_tutoria_command(message):
    eliminar_solicitud_tutoria(bot, message)

@bot.message_handler(commands=['eliminarSolicitudTutor'])
def eliminar_solicitud_tutor_command(message):
    eliminar_solicitud_tutor(bot, message)

@bot.message_handler(commands=['verHistorialTutoriasImpartidas'])
def historial_tutorias_impartidas_command(message):
    obtenerTutoriasEstudianteTutor(message)

@bot.message_handler(commands=['verHistorialTutoriasRecibidas'])
def historial_tutorias_recibidas_command(message):
    obtenerTutoriasEstudianteEstudiante(message)


#Formulario para Ingresar Estudiante
@bot.message_handler(commands=['solicitudEstudiante'])
def crear_solicitud_estudiante(message):
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

#FORMULARIO TUTORIA
def solicitar_tutoria(message):
    try:
        # First, greet the user
        bot.reply_to(message, "Para crear una solicitud, ingresa los siguientes datos:")

        # Get the list of available classes
        url = 'https://localhost:8080/api/clases/'
        
        response = requests.get(url,  verify=False)
        clases = response.json()

        # Display the list of classes to the user
        bot.reply_to(message, "Estas son las clases disponibles:")
        for i, clase in enumerate(clases, start=1):
            id_clase  = clase['_id']
            nombre_clase = clase['nombre_clase']
            codigo_clase = clase['codigo_clase']
            bot.send_message(message.chat.id, f"{i}. Código de clase: {codigo_clase}\nNombre de la clase: {nombre_clase}")

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
            response = requests.get(url,  verify=False)
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
                    horarios_disponibles = "\n ".join(f"{horario['dia']} {horario['hora']}" for horario in tutor['horario_solicitado'])

                    # Mostrar el nombre del tutor y sus horarios disponibles
                    bot.send_message(message.chat.id, f"{i}. Nombre: {nombre}\nHorarios de tutorías: \n{horarios_disponibles}")
                
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
            id_telegram = message.chat.id
            estudiante_id = obtener_id_estudiante(id_telegram)
            # Create the tutorship request
            url = ' https://localhost:8080/api/solicitud_tutoria/crearSolicitudTutoria'
            data = {
                'estudiante': estudiante_id,
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

#FORMULARIO TUTOR
def crear_solicitud_tutor(message, ):
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
            id_clase = clase['_id']
            nombre_clase = clase['nombre_clase']
            codigo_clase = clase['codigo_clase']
            bot.send_message(message.chat.id, f"{i}. Código de clase: {codigo_clase}\nNombre de la clase: {nombre_clase}")

        # Registramos el siguiente paso para manejar la selección de la clase por parte del usuario
        bot.register_next_step_handler(message, handle_clase_selection, clases)

    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")
def handle_clase_selection(message, clases):
    try:
        reply = message.text.strip()
        i = int(reply)
        if i < 1 or i > len(clases):
            bot.reply_to(message, f"Por favor, ingresa un número entre 1 y {len(clases)}.")
            bot.register_next_step_handler(message, handle_clase_selection, clases)
        else:
            clase_id = clases[i - 1]['_id']
            horarios_ids = []

            # Llamamos a la función para mostrar los días disponibles para la clase seleccionada
            mostrar_dias_disponibles(message, clase_id,horarios_ids)

    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un número válido.")
        bot.register_next_step_handler(message, handle_clase_selection, clases)
def mostrar_dias_disponibles(message, clase_id,horarios_ids):
    try:
        # Creamos un diccionario que relacione cada número con su correspondiente día de la semana
        dias_semana = {
            "1": "Lunes",
            "2": "Martes",
            "3": "Miércoles",
            "4": "Jueves",
            "5": "Viernes"
        }

        # Mostramos los días al usuario
        dias_disponibles = "\n".join([f"{i}. {dia}" for i, dia in dias_semana.items()])
        bot.reply_to(message, f"Los días disponibles son:\n{dias_disponibles}\n¿Cuál día deseas seleccionar?")

        # Registramos el siguiente paso para manejar la selección del usuario
        bot.register_next_step_handler(message, handle_day_selection, clase_id, dias_semana,horarios_ids)

    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")
def handle_day_selection(message, clase_id,dias_semana,horarios_ids):
    try:
        # Obtenemos el número de día seleccionado por el usuario
        num_dia = message.text.strip()

        # Verificamos si el número de día seleccionado es válido
        if num_dia not in dias_semana:
            bot.reply_to(message, "Selecciona un número de día válido.")
            return

        # Obtenemos el día correspondiente al número seleccionado
        dia_elegido = dias_semana[num_dia]

        # Llamamos a la función para mostrar los horarios disponibles para el día seleccionado
        mostrar_horarios_disponibles(message, clase_id,dia_elegido,horarios_ids)

    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")
def mostrar_horarios_disponibles(message, clase_id, dia_elegido,horarios_ids):
    try:
        # Llamamos a la API para obtener los horarios disponibles para el día seleccionado
        url = f"https://localhost:8080/api/horario/dia/{dia_elegido}"
        
        response = requests.get(url, verify=False)
        horarios = response.json()['horarios']

        # Si hay horarios disponibles, los mostramos al usuario
        if horarios:
            horarios_disponibles = "\n".join([f"{i}. {horario['hora']}" for i, horario in enumerate(horarios, start=1)])
            bot.reply_to(message, f"Los horarios disponibles para el día {dia_elegido} son:\n{horarios_disponibles}")
            # Registramos el siguiente paso para manejar la selección de opciones del usuario
            bot.reply_to(message, "Por favor, ingresa el número del horario que deseas seleccionar:")
            bot.register_next_step_handler(message, handle_horario_selection, clase_id, horarios,horarios_ids)

        # Si no hay horarios disponibles, lo indicamos al usuario
        else:
            bot.reply_to(message, f"No hay horarios disponibles para el día {dia_elegido}.")

    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot AQUIIIIIIIII")
def handle_horario_selection(message, clase_id, horarios,horarios_ids):
    try:
        reply = message.text.strip()
        i = int(reply)
        if i < 1 or i > len(horarios):
            bot.reply_to(message, f"Por favor, ingresa un número entre 1 y {len(horarios)}.")
            bot.register_next_step_handler(message, handle_horario_selection, clase_id, horarios,horarios_ids)
        else:
            horario_id = horarios[i - 1]['_id']
            horarios_ids.append(horario_id)
            print(horarios_ids)

            reply_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            reply_markup.add(types.KeyboardButton("Sí"))
            reply_markup.add(types.KeyboardButton("No"))
            bot.reply_to(message, "¿Quieres agregar otro horario?", reply_markup=reply_markup)
            bot.register_next_step_handler(message, handle_another_horario, clase_id, horarios_ids)


    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un número válido.")
        bot.register_next_step_handler(message, handle_horario_selection, clase_id, horarios,horarios_ids)


    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot ACAAAAAAAAAAA")

def handle_another_horario(message, clase_id, horarios_ids):
    try:
        reply = message.text.strip().lower()
        if reply == "no":
            # Create the tutor request
            id_telegram = message.chat.id
            estudiante_id = obtener_id_estudiante(id_telegram)
            horarios_ids_str = [str(horario_id) for horario_id in horarios_ids]
            url = 'https://localhost:8080/api/solicitud_tutor/crearSolicitudTutor'

            data = {
                'estudiante': estudiante_id,
                'clase': clase_id,
                'horario_solicitado': horarios_ids_str
            }
            response = requests.post(url, json=data, verify=False)

            if response.status_code == 200:
                bot.reply_to(message, "¡Gracias por crear la solicitud! Pronto nos pondremos en contacto contigo.")
            else:
                bot.reply_to(message, "Ocurrió un error al crear la solicitud. Por favor, intenta de nuevo.")

        elif reply == "sí":
            # Ask the user for another horario ID
            dias_semana = {
            "1": "Lunes",
            "2": "Martes",
            "3": "Miércoles",
            "4": "Jueves",
            "5": "Viernes"
            }

            # Mostramos los días al usuario
            dias_disponibles = "\n".join([f"{i}. {dia}" for i, dia in dias_semana.items()])
            bot.reply_to(message, f"Los días disponibles son:\n{dias_disponibles}\n¿Cuál día deseas seleccionar?")

            # Registramos el siguiente paso para manejar la selección del usuario
            bot.register_next_step_handler(message, handle_day_selection, clase_id, dias_semana,horarios_ids)

        else:
            bot.reply_to(message, "Por favor, ingresa una respuesta válida.")
    except ValueError:
        dias_semana = {
            "1": "Lunes",
            "2": "Martes",
            "3": "Miércoles",
            "4": "Jueves",
            "5": "Viernes"
            }

        # Mostramos los días al usuario
        dias_disponibles = "\n".join([f"{i}. {dia}" for i, dia in dias_semana.items()])
        bot.reply_to(message, f"Los días disponibles son:\n{dias_disponibles}\n¿Cuál día deseas seleccionar?")

        # Registramos el siguiente paso para manejar la selección del usuario
        bot.register_next_step_handler(message, handle_day_selection, clase_id, dias_semana,horarios_ids)



bot.add_message_handler(start)
bot.add_message_handler(crear_solicitud_tutor)
bot.add_message_handler(solicitar_tutoria)
bot.add_message_handler(mostrar_solicitud_tutor)
bot.add_message_handler(mostrar_solicitud_tutoria)
bot.add_message_handler(eliminar_solicitud_tutoria)
bot.add_message_handler(eliminar_solicitud_tutor)
bot.add_message_handler(obtenerTutoriasEstudianteTutor)
bot.add_message_handler(obtenerTutoriasEstudianteEstudiante)
bot.add_message_handler(crear_solicitud_estudiante)
bot.add_message_handler(menu)

bot.infinity_polling()