# importamos todas las librerías necesarias para el programa
import math
import requests
import re
import os
import time
import pandas as pd
import unicodedata
import datetime
from bs4 import BeautifulSoup

ini = time.time()

# BeSoccer tiene antiscraper por lo que declaramos una cabecera html con un user agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
# declaramos todos los arrays necesarios para el posterior dataframe


def ajuste(arr, len):
    return arr[:len]


# primero definimos las competiciones a scrapear (para concatenar luego en el URL)
nombres_competiciones = ["primera", "segunda", "primera_division_rfef",
                         "segunda_division_rfef", "tercera_division_rfef", "galicia", "liga_revelacao", "vitalis", "portugal"]
# segundo necesitamos saber cuántos equipos hay por liga
nombres_equipos = []
# tercero necesitamos saber los URLs de los jugadores a scrapear

urls_jugadores = []
redes_jugadores = []
"""
# find span class action  y que dentro tenga un strong que ponga cesión al o cesion con
nombres_jugadores_cedidos = []

# <td data-content-tab="team_total">
temporadas_jugadores = []
asistencias__totales_jugadores = []
partidos_totales_jugados = []  # <td data-content-tab="tprc1" class="grey">696</td>
tarjetas_totales_jugadores = []

    paginaEquipos = "https://es.besoccer.com/equipo/plantilla/barcelona" """
nombres_jugadores = []
edad_jugadores = []
months = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
          "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


datosExtra = {
    "Minutos jugados": "",
    "Goles": "",
    "Posición principal": "",
    "Posición principal(%)": "",
    "Posición alternativa": "",
    "Posición alternativa(%)": ""
}


def formato(date_string):
    # Translate the month name to English
    month_translations = {
        "enero": "january",
        "febrero": "february",
        "marzo": "march",
        "abril": "april",
        "mayo": "may",
        "junio": "june",
        "julio": "july",
        "agosto": "august",
        "septiembre": "september",
        "octubre": "october",
        "noviembre": "november",
        "diciembre": "december"
    }
    date_string = date_string.replace(
        date_string.split()[1], month_translations[date_string.split()[1]])
    date_object = datetime.datetime.strptime(date_string, "%d %B %Y")
    month_number = date_object.month
    new_date_string = date_string.replace(" ", "/")
    new_date_string = new_date_string.replace(
        date_object.strftime("%B"), f'{month_number:02}')
    return new_date_string


def arregla(arr):
    new_arr = []
    for element in arr:
        # Remove diacritics (accents)
        element = unicodedata.normalize(
            'NFKD', element).encode('ASCII', 'ignore').decode()
        # Replace spaces and certain text with underscores
        element = re.sub(
            r"\s|R\.|RC Deportivo\.|RC\.|RM\.|AD Mérida\.", "_", element)
        new_arr.append(element)
    return new_arr


# diccionario vacío con las etiquetas como clave
datos = {
    "Nombre": "",
    "Fecha nacimiento": "",
    "Localidad nacimiento": "",
    "País nacimiento": "",
    "Continente nacimiento": "",
    "Región de nacimiento": "",
    "Demarcación": "",
    "Pierna predominante": "",
    "ELO": "",
    "Potencial": "",
    "Equipo actual": "",
    "Competición principal": "",
    "Equipo anterior": "",
    "Competición anterior": "",
    "Dorsal más común": "",
    "Otros dorsales": "",
    "Etapa juveniles": "",

}

# obtenemos los nombres de los equipos para poder recorrer luego cada uno por sus jugadores
for competicion in nombres_competiciones:
    paginaCompeticiones = "https://es.besoccer.com/competicion/clasificacion/" + \
        competicion+"/2023"
    respuestaCompeticiones = requests.get(paginaCompeticiones, headers=headers)
    htmlCompeticiones = BeautifulSoup(
        respuestaCompeticiones.content, 'html.parser')
    """consultas para este URL:
    obtener el valor de las etiquetas <span> con class team.name
    """
    nombresEquipos = htmlCompeticiones.find_all('span', {"class": "team-name"})

    for nombre_equipo in nombresEquipos:
        nombres_equipos.append(nombre_equipo.text)
# obtenemos las URLs de los jugadores recorriendo cada equipo
# for equipo in nombres_equipos:
    # paginaEquipos = "https://es.besoccer.com/equipo/plantilla/" + \
     #   equipo + "/#team_performance"
    paginaEquipos = "https://es.besoccer.com/equipo/plantilla/barcelona"
    respuestaEquipos = requests.get(paginaEquipos, headers=headers)
    htmlEquipos = BeautifulSoup(respuestaEquipos.content, 'html.parser')
    """consultas para este URL:
    obtener el valor de las etiquetas <a> con class name
    """
    for td in htmlEquipos.find_all("td", {"class": "name"}):
        url_jugador = td.find("a", href=True)["href"]
        urls_jugadores.append(url_jugador)

# ahora trabajaremos con cada jugador
datos_jugadores = []
for urljugador in urls_jugadores:
    respuestaJugadores = requests.get(urljugador, headers=headers)
    htmlJugadores = BeautifulSoup(respuestaJugadores.content, 'html.parser')
    dataPanelTitle = htmlJugadores.find("div", id="mod_player_stats")
    divDataPanelTitle = htmlJugadores.find('div', class_="panel-title")

    redesJugadores = htmlJugadores.find('div', class_="main-text break-url")
    if redesJugadores is not None:
        for div in redesJugadores:
            redes_jugadores.append(div.text)
    else:
        redes_jugadores.append(None)
    divDataPanelHead = htmlJugadores.find('div', class_="panel-head")

    posicionJugadores = htmlJugadores.find('div', class_="role-box")
    datosMayores = htmlJugadores.find('div', class_="main-line")

    if datosMayores is not None:
        for div in datosMayores:
            datos_jugadores.append(div.text)
    else:
        datos_jugadores(None)

    for div in divDataPanelTitle:
        nombres_jugadores.append(div.text)

    for div in datosMayores:
            """ 
            if not elements.isspace() and divText.text != "":
                if divText.next_siblings == "Minutos jugados" or divText.next_siblings == "Goles/90": """
            print(div.text)
            datosExtra.append(div.text)
    #print(datosExtra)
    nombres_jugadores = [n for i, n in enumerate(
        nombres_jugadores) if n not in nombres_jugadores[:i]]
    divDataTableList = htmlJugadores.find_all("div", class_="table-row")
    datos = {}
    datos.update({"URL:": urljugador})
    for div in divDataTableList:
        divText = div.find('div')
        for elements in divText.next_siblings:
            try:
                if not elements.isspace() and divText.text != "":
                    if divText.text.strip() == "Fecha nacimiento":
                        fecha_nacimiento = datetime.datetime.strptime(
                            elements.text.strip(), "%d/%m/%Y")
                        hoy = datetime.datetime.now()
                        edad = hoy.year - fecha_nacimiento.year - \
                            ((hoy.month, hoy.day) <
                             (fecha_nacimiento.month, fecha_nacimiento.day))

                    else:
                        datos[divText.text.strip()] = elements.text.strip()
                        link = elements.find("a", class_="image-row link")
                        if link is not None:
                            datos[link.text] = link["href"]
            except TypeError:
                datos[divText.text.strip()] = elements.text.strip()
    if datos["Fecha nacimiento"] != "":
        fe_nac = datetime.datetime.strptime(
            formato(datos["Fecha nacimiento"]), "%d/%B/%Y")
        edad = (datetime.datetime.now() - fe_nac).days / 365
    else:
        edad = None
    datos_jugadores.append(datos)
    edad_jugadores.append(math.trunc(edad))
df = pd.DataFrame(datos_jugadores)
edad_jugadores = ajuste(edad_jugadores, len(nombres_jugadores))
datos_jugadores = ajuste(datos_jugadores, len(nombres_jugadores))
""" print(edad_jugadores)
print(datos_jugadores) """
df.drop_duplicates(inplace=True)
df.insert(loc=1, column='Temporada', value="2022/23")
df.insert(loc=2, column='Equipo', value=ajuste(
    nombres_equipos, len(nombres_jugadores)))
df.insert(loc=3, column='Edad', value=edad_jugadores)
df.insert(loc=4, column='Nombre', value=nombres_jugadores)
df.insert(loc=18, column='Twitter', value=redes_jugadores)

df = df.reindex(columns=['URL:', 'Temporada', 'Equipo', 'Edad', 'Nombre',
                         'Fecha nacimiento', 'Localidad nacimiento', 'Demarcación', 'Pierna predominante',  'ELO',
                         'Potencial', 'Competición principal', 'Competición anterior',
                         'Equipo anterior', 'Fin contrato', 'Valor mercado', 'Goles', 'Minutos jugados', 'Agente', 'Salario',
                         'Twitter', 'Posición principal', 'Posición principal (%)', 'Posición alternativa', 'Posición alternativa (%)'])
print(df)
# exportar el dataframe a .csv
df.to_csv(os.path.expanduser('~/Desktop\\') + r' jugadores.csv',
          index=False, header=True)
fin = time.time()

m, s = divmod(fin-ini, 60)
print(f"Tiempo de ejecución: {m:.0f} minuto(s) y {s:.2f} segundo(s)")
