import os
import telebot
from dotenv import load_dotenv
import requests
from telebot import types


load_dotenv()

BOT_TOKEN = os.environ.get('TELEGRAM_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

#/verHistorialTutoriasImpartidas
def obtenerTutoriasEstudianteTutor(message):
    try:
        End_Point = os.environ.get('API_URL')
        url = f'https://localhost:8080/api/tutoria/obtenerTutoriasEstudianteTutor/{message.chat.id}'
        bot.reply_to(message, "Tutorias impartidas:")
        response = requests.get(url, verify=False)
        data = response.json()
        tutoriasimpartidas_list = []
        if(response.status_code == 200):
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
        elif(response.status_code == 404):
            bot.send_message(message.chat.id, "Usted es un estudiante, por lo tanto no tiene tutorias impartidas")
    except Exception as e:
        bot.send_message(message.chat.id, "Error al obtener las tutorias " + str(e))

#/verHistorialTutoriasRecibidasdef obtenerTutoriasEstudianteEstudiante(message):
def obtenerTutoriasEstudianteEstudiante(message):
    try:
        End_Point = os.environ.get('API_URL')
        url = f'https://localhost:8080/api/tutoria/obtenerTutoriasEstudianteEstudiante/{message.chat.id}'
        bot.reply_to(message, "Tutorias recibidas:")
        response = requests.get(url, verify=False)
        data = response.json()
        tutoriasimpartidas_list = []
        if(response.status_code == 200):
            for tutoria in data:
                numerocuenta = tutoria['numerocuenta']
                nombreestudiante = tutoria['nombreestudiante']
                materia = tutoria['clase']
                codigomateria = tutoria['codigoclase']
                dia = tutoria['dia']
                hora = tutoria['hora']
                aula = tutoria['aula']
                nombretutor = tutoria['nombretutor']
                numerocuentatutor = tutoria['numerocuentatutor']
                active = tutoria['activa']
                tutoriasimpartidas_list.append({
                    'numerocuenta': numerocuenta,
                    'nombreestudiante': nombreestudiante,
                    'materia': materia,
                    'codigomateria': codigomateria,
                    'dia': dia,
                    'hora': hora,
                    'aula': aula,
                    'nombretutor': nombretutor,
                    'numerocuentatutor': numerocuentatutor,
                    'active': active
                })
            for tutoria_data in tutoriasimpartidas_list:
                numerocuenta = tutoria_data['numerocuenta']
                bot.send_message(message.chat.id, f"Numero de cuenta: {numerocuenta}\nNombre del Estudiante: {tutoria_data['nombreestudiante']}\nMateria: {tutoria_data['materia']}\nCodigo de la materia: {tutoria_data['codigomateria']}\nNombre del Tutor: {tutoria_data['nombretutor']}\nNumero de cuenta del Tutor: {tutoria_data['numerocuentatutor']}\nDía: {tutoria_data['dia']}\nHora: {tutoria_data['hora']}\nAula: {tutoria_data['aula']}\nActiva: {tutoria_data['active']}")
        elif(response.status_code == 404):
            bot.send_message(message.chat.id, "Usted es un tutor, por lo tanto no tiene tutorias recibidas")
    except Exception as e:
        bot.send_message(message.chat.id, "Error al obtener las tutorias")