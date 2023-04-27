import os
import telebot
from dotenv import load_dotenv
import requests
from telebot import types


load_dotenv()

BOT_TOKEN = os.environ.get('TELEGRAM_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

#/verHistorialTutoriasImpartidas
def obtenerTutoriasEstudianteTutor(message,token):
    try:
        End_Point = os.environ.get('API_URL')
        url = '{}tutoria/obtenerTutoriasEstudianteTutor'.format(End_Point)
        headers = {
            'Authorization': 'Bearer ' + token
        }
        bot.reply_to(message, "Tutorias impartidas:")
        print(token)
        response = requests.get(url, headers=headers, verify=False)
        data = response.json()
        tutoriasimpartidas_list = []
        for tutoria in data:
            numerocuenta = tutoria['numerocuenta']
            nombretutor = tutoria['nombretutor']
            materia = tutoria['clase']
            codigomateria = tutoria['codigoclase']
            active = tutoria['activa']
            tutoriasimpartidas_list.append({
                'numerocuenta': numerocuenta,
                'nombretutor': nombretutor,
                'materia': materia,
                'codigomateria': codigomateria,
                'active': active
            })
        for tutoria_data in tutoriasimpartidas_list:
            numerocuenta = tutoria_data['numerocuenta']            
            bot.send_message(message.chat.id, f"Numero de cuenta: {numerocuenta}\nNombre del tutor: {tutoria_data['nombretutor']}\nMateria: {tutoria_data['materia']}\nCodigo de la materia: {tutoria_data['codigomateria']}\nActiva: {tutoria_data['active']}")
    except Exception as e:
        bot.send_message(message.chat.id, "Error al obtener las tutorias ")

#/verHistorialTutoriasRecibidas
def obtenerTutoriasEstudianteEstudiante(message,token):
    try:
        End_Point = os.environ.get('API_URL')
        url = '{}tutoria/obtenerTutoriasEstudianteEstudiante'.format(End_Point)
        bot.reply_to(message, "Tutorias impartidas:")
        response = requests.get(url, verify=False)
        data = response.json()
        tutoriasimpartidas_list = []
        for tutoria in data:
            numerocuenta = tutoria['numerocuenta']
            nombreestudiante = tutoria['nombreestudiante']
            materia = tutoria['clase']
            codigomateria = tutoria['codigoclase']
            active = tutoria['activa']
            tutoriasimpartidas_list.append({
                'numerocuenta': numerocuenta,
                'nombreestudiante': nombreestudiante,
                'materia': materia,
                'codigomateria': codigomateria,
                'active': active
            })
        for tutoria_data in tutoriasimpartidas_list:
            numerocuenta = tutoria_data['numerocuenta']
            bot.send_message(message.chat.id, f"Numero de cuenta: {numerocuenta}\nNombre del Estudiante: {tutoria_data['nombreestudiante']}\nMateria: {tutoria_data['materia']}\nCodigo de la materia: {tutoria_data['codigomateria']}\nActiva: {tutoria_data['active']}")
    except Exception as e:
        bot.reply_to(message, "Error al obtener las tutorias" + str(e))