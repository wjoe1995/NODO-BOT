import requests

# Función para obtener el id_estudiante a partir del id_telegram
def obtener_id_estudiante(id_telegram):
    try:
        url = f'https://localhost:8080/api/estudiantes/extraer/{id_telegram}'
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            estudiante = response.json()
            return estudiante['_id']
        else:
            print(f"Error al obtener el id_estudiante para el id_telegram {id_telegram}.")
            print(response.content)
            return None
    except Exception as e:
        print(f"Error al obtener el id_estudiante para el id_telegram {id_telegram}.")
        print(e)
        return None

