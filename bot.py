import os
import telebot
from dotenv import load_dotenv
import requests
from telebot import types
import subprocess

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
        "start": "/start",
        #"aulas": "/aulas",
        #"usuarios": "/usuarios",
        "Solicitud de Registro de Estudiantes": "/solicitudRegistroEstudiantes",
        "Tutorias": {
            "Ver mi historial de tutorias recibidas": "/verHistorialTutoriasRecibidas",
            "Ver tutorias activas": "/verTutoriasActivas",
            "Solicitar tutoria": {
                "Formulario de solicitud": "/solicitarTutoria",
                "Ver estado de solicitud": "/verEstadoSolicitudTutoria",
                "Ver historial tutorias recibidas": "/verHistorialTutoriasRecibidas",
                "Ver tutorias activas": "/verTutoriasActivas",
                "Regresar": "back"
            },
            "Solicitar ser tutor": {
                "Formulario de solicitud": "/solicitarSerTutor",
                "Ver estado de solicitud": "/verEstadoSolicitudSerTutor",
                "Ver Tutorias Impartidas": "/verTutoriasImpartidas",
                "Ver Tutorias Activas": "/verTutoriasActivas",
                "Regresar": "back"
            },
            "Regresar": "back"
        }
        
    }
    menu_interactivo(message.chat.id, opciones.keys())
    print(message.chat.id)
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
def usuarios(message):
    try:
        url = 'https://localhost:8080/api/usuarios/obtenerUsuarios'
        bot.reply_to(message, "Usuarios registrados:")
        response = requests.get(url, verify=False)
        data = response.json()
        usuarios_dict = {}
        for usuario in data:
            nombre_usuario = usuario['nombre_usuario']
            password = usuario['password']
            nombre_rol = usuario['rol']['nombre_rol']
            descripcion_permisos = ', '.join(permiso['descripcion'] for permiso in usuario['rol']['permisos'])
            usuarios_dict[nombre_usuario] = {'password': password, 'nombre_rol': nombre_rol, 'descripcion_permisos': descripcion_permisos}
        for nombre_usuario, usuario_data in usuarios_dict.items():
            bot.send_message(message.chat.id, f"Usuario: {nombre_usuario}\nPassword: {usuario_data['password']}\nRol: {usuario_data['nombre_rol']}\nPermisos: {usuario_data['descripcion_permisos']}")
    except Exception as e:
        bot.reply_to(message, "Error al obtener los usuarios" + str(e))

bot.add_message_handler(start)
bot.add_message_handler(aulas)
bot.add_message_handler(usuarios)
bot.add_message_handler(menu)

bot.infinity_polling()
