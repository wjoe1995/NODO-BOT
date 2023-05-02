def mostrar_carreras_disponibles(message,horarios_ids):
    try:
        # Creamos un diccionario que relacione cada número con su correspondiente día de la semana
        carreras = {
            "1": "Ingeniería en Sistemas",
            "2": "Ingeniería Agroindustrial",
            "3": "Ingeniería Acuícola",
            "4": "Administración de Empresas",
        }

        # Mostramos los días al usuario
        carreras = "\n".join([f"{i}. {carrera}" for i, carrera in carreras.items()])
        bot.reply_to(message, f"Las Carreras disponibles son:\n{carreras}\n¿Cuál día deseas seleccionar?")

        # Registramos el siguiente paso para manejar la selección del usuario
        bot.register_next_step_handler(message, handle_day_selection, carreras)

    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")

def handle_day_selection(message, carreras):
    try:
        # Obtenemos el número de día seleccionado por el usuario
        num_carrera = message.text.strip()

        # Verificamos si el número de día seleccionado es válido
        if num_carrera not in carreras:
            bot.reply_to(message, "Selecciona un número de día válido.")
            return

        # Obtenemos el día correspondiente al número seleccionado
        carrera_elegido = carreras[num_carrera]

        # Llamamos a la función para mostrar los horarios disponibles para el día seleccionado
        crear_solicitud_tutor(message, carrera_elegido)

    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al llamar al bot")

def crear_solicitud_tutor(message,carrera_elegido ):
    try:
        # First, greet the user
        bot.reply_to(message, "Para crear una solicitud, ingresa los siguientes datos:")

        # Get the list of available classes
        url = f"https://localhost:8080/api/clases/carrera/{carrera_elegido}"

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
        bot.reply_to(message, f"Por favor, ingresa un valor de 1 al {len(clases)} para elegir la clase que deseas agregar")
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
                bot.reply_to(message, f"Regrese al menú haciendo click en /menu ") 
            elif response.status_code == 400:
                bot.reply_to(message, "¡Esta haciendo un registro que ya existe! Ya solicito esa clase antes")
                bot.reply_to(message, "Regrese al menú haciendo click en /menu y revise el estado de su solicitud")
            else:
                bot.reply_to(message, "Ocurrió un error al crear la solicitud. Por favor, intenta de nuevo.")
                bot.reply_to(message, f"Regrese al menú haciendo click en /menu ") 

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
