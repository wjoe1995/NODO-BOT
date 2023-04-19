import os
import telebot
from dotenv import load_dotenv
import requests

load_dotenv()


BOT_TOKEN = os.environ.get('TELEGRAM_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

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
        numeros = ", ".join(aula["numero"] for aula in data)
        bot.send_message(message.chat.id, f"Aquí están los números de aula disponibles: {numeros}")
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

bot.infinity_polling()
