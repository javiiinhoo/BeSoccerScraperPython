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


def rellenar_array(arr, value, length):
    # Obtenemos la diferencia entre la longitud actual y la deseada
    diff = length - len(arr)

    # Agregamos el valor al array la cantidad de veces necesarias
    for i in range(diff):
        arr.append(value)


# primero definimos las competiciones a scrapear (para concatenar luego en el URL)
nombres_competiciones = ["portugal"]
"""
, "segunda", "primera_division_rfef",
                         "segunda_division_rfef", "tercera_division_rfef", "galicia", "liga_revelacao", "vitalis", "portugal"]"""
""""""

# segundo necesitamos saber cuántos equipos hay por liga
nombres_equipos = []
# tercero necesitamos saber los URLs de los jugadores a scrapear

urls_jugadores = []
equipo_jugadores = []
urls_equipos = []
redes_jugadores = []
df_final = pd.DataFrame()
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


datosExtra = {}


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


c = ["País nacimiento", "Continente nacimiento", "Región de nacimiento",
     "Nacionalidad(es)", "Dorsal más común", "Otros dorsales", "Etapa juveniles",
     "Valor máximo en su carrera", "General", "Su edad", "En su país", "En su posición",
     "En su demarcación", "Proveedor", "Inicio contrato", "Traspasos", "Valor TM",
     "Valor CIES", "Cláusula resc.", "Veces convocado", "Partidos titular",
     "Desde el banquillo", "Debut", "Edad de debut", "Último partido",
     "Edad en último partido", "Tarjeta Amarilla", "Últ. renovación",
     "Gol", "Último traspaso", "Total traspasos", "Asistencia de gol", "Tiro al palo", "Equipo actual"]

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

nuevos_nombres_columnas = {
    'URL': 'URL:',
    'Temporada': 'Temporada',
    'Equipo': 'Equipo',
    'Edad': 'Edad',
    'Nombre': 'nombre',
    'Fecha nacimiento': 'Fecha nacimiento',
    'Localidad nacimiento': 'Lugar nacimiento',
    'Demarcación': 'demarcacion',
    'Pierna predominante': 'pierna',
    'ELO': 'elo',
    'Potencial': 'potencial',
    'Competición principal': 'Competicion',
    'Equipo anterior': 'Equipo anterior',
    'Competición anterior': 'Competicion anterior',
    'Agente': 'Agente',
    'Fin contrato': 'Fin de Contrato',
    'Valor mercado': 'Valor de Mercado',
    'Salario': 'Salario',
    'MinutosJugados': 'MinutosJugados',
    'Goles': 'Goles',
    'Twitter': 'Twitter',
    'Posición principal': 'Posicion principal',
    'Posición princ %': 'Posicion princ %',
    'Posición Alternativa': 'Posicion Alternativa',
    'Posición alternativa(%)': 'Posicion Altern%'
}
occurrences = {}

# obtenemos los nombres de los equipos para poder recorrer luego cada uno por sus jugadores
for competicion in nombres_competiciones:
    paginaCompeticiones = f"https://es.besoccer.com/competicion/clasificacion/{competicion}/2023"
    respuestaCompeticiones = requests.get(paginaCompeticiones, headers=headers)
    htmlCompeticiones = BeautifulSoup(
        respuestaCompeticiones.content, 'html.parser')
    nombresEquipos = htmlCompeticiones.find_all('td', {"class": "name"})

for equipo in nombresEquipos:
    nombre_equipo = equipo.find("span", {"class": "team-name"}).text
    if nombre_equipo in occurrences:
        occurrences[nombre_equipo] += 1
    else:
        occurrences[nombre_equipo] = 1

    url = equipo.find("a", href=True)["href"]
    url_equipo = url.replace("equipo", "equipo/plantilla")
    urls_equipos.append(url_equipo)
equipos_rep = []
# obtenemos las URLs de los jugadores recorriendo cada equipo
for url_equipo in urls_equipos:
    respuestaEquipos = requests.get(url_equipo, headers=headers)
    htmlEquipos = BeautifulSoup(respuestaEquipos.content, 'html.parser')
    jugadores = htmlEquipos.find_all("td", {"class": "name"})
    nombre_equipo = htmlEquipos.find("h2", {"class": "title ta-c"}).text
    for i in range(len(jugadores)):
        equipos_rep.append(nombre_equipo)

    for jugador in jugadores:
        url_jugador = jugador.find("a", href=True)["href"]
        urls_jugadores.append(url_jugador)
print(equipos_rep)

# ahora trabajaremos con cada jugador
datos_jugadores = []
for urljugador in urls_jugadores:
    respuestaJugadores = requests.get(urljugador, headers=headers)
    htmlJugadores = BeautifulSoup(respuestaJugadores.content, 'html.parser')
    dataPanelTitle = htmlJugadores.find("div", id="mod_player_stats")
    divDataPanelTitle = dataPanelTitle.find('div', class_="panel-title")
    nombres_jugadores.append(divDataPanelTitle.text)

    redesJugadores = htmlJugadores.find('div', class_="desc-boxes")
    twitter_url = None
    if redesJugadores:
        twitter = redesJugadores.find_all(
            'div', class_=["sub-text2", "break-url"])
        for sub, url in zip(twitter[::2], twitter[1::2]):
            if sub.text.strip() == 'Twitter':
                twitter_url = url.text
                break
    redes_jugadores.append(twitter_url)

    for item_col in htmlJugadores.find_all('div', class_='compare-box'):

        main_role = item_col.find('div', class_="main-role")
        other_roles = item_col.find('ul', class_="position-list")

        if main_role:
            role_span = main_role.find_all('span')
            if role_span:
                datosExtra["Posición principal"] = role_span[0].text
                datosExtra["Posición princ %"] = role_span[1].text
        else:
            datosExtra["Posición principal"] = None
            datosExtra["Posición princ %"] = None

        if other_roles:
            other_role = other_roles.find_all('li')
            if other_role:
                for element in other_role:
                    text_split = element.text.strip().split('\n')
                    posicion = text_split[0]
                    porcentaje = text_split[1]
                    datosExtra["Posición Alternativa"] = posicion
                    datosExtra["Posicion Altern%"] = porcentaje
        else:
            datosExtra["Posición Alternativa"] = None
            datosExtra["Posición Altern%"] = None

    for item_col in htmlJugadores.find_all('div', class_='item-col'):
        main_line = item_col.find('div', class_='main-line')
        other_line = item_col.find('div', class_='other-line')
        if main_line and other_line:
            other_line_texts = other_line.find_all('div')
            if len(other_line_texts) > 1:
                minutes = None
                goals = None
                for other_line_text in other_line_texts:
                    text = other_line_text.text.strip()
                    if text == "Minutos":
                        datosExtra["MinutosJugados"] = main_line.text.replace(
                            "'", "")
                    elif text == "Goles/90'":
                        datosExtra["Goles"] = main_line.text
        for div in divDataPanelTitle:
            nombres_jugadores.append(div.text)
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
                                ((hoy.month, hoy.day) < (
                                    fecha_nacimiento.month, fecha_nacimiento.day))
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
    edad_jugadores.append(math.trunc(edad))
    # print(edad_jugadores)
    datos.update(datosExtra)
    datos_jugadores.append(datos)
for d in datos_jugadores:
    for col in c:
        d.pop(col, None)

    for dict in datos_jugadores:
        dict['Edad'] = edad_jugadores
        dict['Temporada'] = "2022/23"
        dict['Equipo'] = equipos_rep
        dict['Nombre'] = nombres_jugadores
        dict['Twitter'] = redes_jugadores
    df = pd.DataFrame(datos_jugadores)


df = df.rename(columns=nuevos_nombres_columnas)

# reorder columns
df = df[['URL:', 'Temporada', 'Equipo', 'Edad', 'nombre', 'Fecha nacimiento',
        'Lugar nacimiento', 'demarcacion', 'pierna', 'elo', 'potencial',
         'Competicion', 'Competicion anterior', 'Equipo anterior', 'Fin de Contrato',
         'Valor de Mercado', 'Goles', 'MinutosJugados', 'Agente', 'Salario', 'Twitter', 'Posicion principal',
         'Posicion princ %', 'Posicion Alternativa', 'Posicion Altern%']]


df.to_csv(os.path.expanduser('~/Desktop\\') + r' jugadores.csv',
          index=False, header=True)

fin = time.time()

m, s = divmod(fin-ini, 60)
print(f"Tiempo de ejecución: {m:.0f} minuto(s) y {s:.2f} segundo(s)")
