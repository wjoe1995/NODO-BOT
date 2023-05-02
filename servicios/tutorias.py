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
                bot.send_message(message.chat.id, f"Número de cuenta: {numerocuenta}\nNombre del tutor: {tutoria_data['nombretutor']}\nMateria: {tutoria_data['materia']}\Código de la materia: {tutoria_data['codigomateria']}\nActiva: {tutoria_data['active']}")
        elif(response.status_code == 404):
            bot.send_message(message.chat.id, "Usted es un estudiante, por lo tanto no tiene tutorias impartidas")
    except Exception as e:
        bot.send_message(message.chat.id, "Error al obtener las tutorias " + str(e))

#/verHistorialTutoriasRecibidasdef obtenerTutoriasEstudianteEstudiante(message):
def obtenerTutoriasEstudianteEstudiante(message):
    try:
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
        elif(response.status_code == 404):
            bot.send_message(message.chat.id, "Usted es un tutor, por lo tanto no tiene tutorias recibidas")
    except Exception as e:
        bot.send_message(message.chat.id, "Error al obtener las tutorias")

def obtenerTutoriasDisponibles(message):
    url = f'https://localhost:8080/api/tutoria/obtenerTutoriasDisponibles'
    bot.reply_to(message, "Tutorias Disponibles:")
    response = requests.get(url, verify=False)
    data = response.json()
    tutoriasdisponibles_list = []
    if(response.status_code == 200):
        for tutoria in data:
            aula = tutoria['aula']['numero']
            nombre_clase = tutoria['solicitud_tutoria']['clase']['nombre_clase']
            codigo_clase = tutoria['solicitud_tutoria']['clase']['codigo_clase']
            nombre_carrera_clase = tutoria['solicitud_tutoria']['clase']['carrera']['nombre_carrera']
            dia_solicitado = tutoria['solicitud_tutoria']['horario_solicitado'][0]['dia']
            hora_solicitada = tutoria['solicitud_tutoria']['horario_solicitado'][0]['hora']
            nombre_tutor = tutoria['solicitud_tutoria']['tutor']['nombre']
            numero_cuenta_tutor = tutoria['solicitud_tutoria']['tutor']['numero_cuenta']
            carrera_tutor = tutoria['solicitud_tutoria']['tutor']['carrera']['nombre_carrera']
            telefono_tutor = tutoria['solicitud_tutoria']['tutor']['telefono']
            tutoriasdisponibles_list.append({
                'aula': aula,
                'nombre_clase': nombre_clase,
                'codigo_clase': codigo_clase,
                'nombre_carrera_clase': nombre_carrera_clase,
                'dia_solicitado': dia_solicitado,
                'hora_solicitada': hora_solicitada,
                'nombre_tutor': nombre_tutor,
                'numero_cuenta_tutor': numero_cuenta_tutor,
                'carrera_tutor': carrera_tutor,
                'telefono_tutor': telefono_tutor
            })
        for tutoria_data in tutoriasdisponibles_list:
            bot.send_message(message.chat.id, f"Aula: {tutoria_data['aula']}\nNombre de la Clase: {tutoria_data['nombre_clase']}\nCódigo de la Clase: {tutoria_data['codigo_clase']}\nNombre de la Carrera: {tutoria_data['nombre_carrera_clase']}\nDía Disponible: {tutoria_data['dia_solicitado']}\nHora Disponible: {tutoria_data['hora_solicitada']}\nNombre del Tutor: {tutoria_data['nombre_tutor']}\nNúmero de cuenta del Tutor: {tutoria_data['numero_cuenta_tutor']}\nCarrera del Tutor: {tutoria_data['carrera_tutor']}\nTeléfono del Tutor: {tutoria_data['telefono_tutor']}\n")
    elif(response.status_code == 404):
        bot.send_message(message.chat.id, "No hay tutorias disponibles")