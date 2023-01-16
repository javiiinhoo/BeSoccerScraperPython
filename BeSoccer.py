# importamos todas las librerías necesarias para el programa
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

start_time = time.time()

# BeSoccer tiene antiscraper por lo que declaramos una cabecera html con un user agent


headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}


# declaramos todos los arrays necesarios para el posterior dataframe

# primero definimos las competiciones a scrapear (para concatenar luego en el URL)
nombres_competiciones = ["primera"]
""", "segunda", "primera_division_rfef",
                         "segunda_division_rfef", "tercera_division_rfef", "galicia", "liga_revelacao", "vitalis", "portugal"""
# segundo necesitamos saber cuántos equipos hay por liga
nombres_equipos = []
# tercero necesitamos saber los URLs de los jugadores a scrapear

urls_jugadores = []

nombres_jugadores = []

temporada_jugadores = []
pais_jugadores = []

# altura para dfcentral o portero

fecha_nac_jugadores = []
lugar_nac_jugadores = []
demarcacion_jugadores = []
pierna_jugadores = []
altura_jugadores = []
elo_jugadores = []
potencial_jugadores = []
equipo_actual_jugadores = []
competicion_actual_jugadores = []
equipo_anterior_jugadores = []
competicion_anterior_jugadores = []
fin_contrato = []
valor_jugadores = []
goles__totales_jugadores = []

minutos_jugados_jugadores = []
agente_jugadores = []
salario_jugadores = []
twitter_jugadores = []
posicion_principal_jugadores = []
posicion_principal_jugadores_porcentaje = []
posicion_alternativa_jugadores = []
posicion_alternativa_jugadores_porcentaje = []
df = pd.DataFrame()
# diccionario vacío con las etiquetas como clave
datos = {
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
    "Etapa juveniles": ""
}
"""
# find span class action  y que dentro tenga un strong que ponga cesión al o cesion con
nombres_jugadores_cedidos = []

# <td data-content-tab="team_total">
temporadas_jugadores = []
asistencias__totales_jugadores = []
partidos_totales_jugados = []  # <td data-content-tab="tprc1" class="grey">696</td>
tarjetas_totales_jugadores = [] """


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
#for equipo in nombres_equipos:
    paginaEquipos = "https://es.besoccer.com/equipo/plantilla/barcelona"
        #equipo+"#team_performance" + \
    respuestaEquipos = requests.get(paginaEquipos, headers=headers)
    htmlEquipos = BeautifulSoup(respuestaEquipos.content, 'html.parser')
    """consultas para este URL:
    obtener el valor de las etiquetas <a> con class name
    """
    for td in htmlEquipos.find_all("td", {"class": "name"}):
        url_jugador = td.find("a", href=True)["href"]
        urls_jugadores.append(url_jugador)

# ahora trabajaremos con cada jugador
for urljugador in urls_jugadores:
    respuestaJugadores = requests.get(urljugador, headers=headers)
    htmlJugadores = BeautifulSoup(respuestaJugadores.content, 'html.parser')

# elemento padre que contiene la información
    dataPanelTitle = htmlJugadores.find("div", id="mod_player_stats")
    divDataPanelTitle=htmlJugadores.find('div', class_="panel-title")
    for div in divDataPanelTitle:
        nombres_jugadores.append(div.text)
    # find_all para buscar todos los elementos 'div'
    divDataTableList = htmlJugadores.find_all("div", class_="table-row")    
    for div in divDataTableList:
        divText = div.find('div')
        for elements in divText.next_siblings:
            try:
                if not elements.isspace() and divText.text != "":
                    # Usa el diccionario para buscar la etiqueta correspondiente
                    datos[divText.text.strip()] = elements.text.strip()
                    link = elements.find("a", class_="image-row link")
                    if link is not None:
                        datos[link.text] = link["href"]
            except TypeError:
                datos[divText.text.strip()] = elements.text.strip()
    print(nombres_jugadores)
    df_nombres = pd.DataFrame(nombres_jugadores, columns=["Nombre del jugador"])

    #divDataPanelList = htmlJugadores.find_all("div", class_="big-row")
    datos = {k: v.strip().replace("\n", ",").replace("  ", "")
             for k, v in datos.items()}
    # convierta el diccionario a un dataframe
    df_temp = pd.DataFrame.from_dict(datos,orient='index').T
# Concatenar todos los diccionarios en un DataFrame
    df = pd.concat([df, df_temp], ignore_index=True)
    df = pd.concat([df_nombres, df], ignore_index=True)

print(df)

# exportar el dataframe a .csv
df.to_csv(os.path.expanduser('~/Desktop\\') + r' urls.csv',
          index=False, header=True)
end_time = time.time()


minutes, seconds = divmod(end_time-start_time, 60)
print(f"Tiempo de ejecución: {minutes:.0f} minutos y {seconds:.2f} segundos")
