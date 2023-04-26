import os
import telebot
from dotenv import load_dotenv
import requests
from telebot import types

load_dotenv()

BOT_TOKEN = os.environ.get('TELEGRAM_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

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