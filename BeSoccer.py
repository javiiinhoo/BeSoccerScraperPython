# importamos todas las librerías necesarias para el programa
import requests,re,os,time,pandas as pd,unicodedata
from bs4 import BeautifulSoup

ini = time.time()

# BeSoccer tiene antiscraper por lo que declaramos una cabecera html con un user agent


headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}


# declaramos todos los arrays necesarios para el posterior dataframe

# primero definimos las competiciones a scrapear (para concatenar luego en el URL)
nombres_competiciones = ["primera"]
# segundo necesitamos saber cuántos equipos hay por liga
nombres_equipos = []
# tercero necesitamos saber los URLs de los jugadores a scrapear

urls_jugadores = []

nombres_jugadores = []
def arregla(arr):
    new_arr = []
    for element in arr:
        # Remove diacritics (accents)
        element = unicodedata.normalize('NFKD', element).encode('ASCII', 'ignore').decode()
        # Replace spaces with underscores
        element = re.sub(r"\s", "_", element)
        # Replace "R." with "real"
        element = re.sub("R\.", "real", element)
        new_arr.append(element)
    return new_arr
"""
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
posicion_alternativa_jugadores_porcentaje = [] """


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
print(nombres_equipos)
arregla(nombres_equipos)
# obtenemos las URLs de los jugadores recorriendo cada equipo
for equipo in nombres_equipos:
    paginaEquipos = "https://es.besoccer.com/equipo/plantilla/" + \
        equipo + "/#team_performance"
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
    df_final = pd.DataFrame()
    # elemento padre que contiene la información
    dataPanelTitle = htmlJugadores.find("div", id="mod_player_stats")
    divDataPanelTitle = htmlJugadores.find('div', class_="panel-title")
    for div in divDataPanelTitle:
        nombres_jugadores.append(div.text)
    # find_all para buscar todos los elementos 'div'
    divDataTableList = htmlJugadores.find_all("div", class_="table-row")
    datos = {}
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
    datos_jugadores.append(datos)
    df_final = pd.DataFrame(datos_jugadores)
    df_final.insert(loc=0, column='Nombre', value=nombres_jugadores)
    print(df_final)
# exportar el dataframe a .csv
df_final.to_csv(os.path.expanduser('~/Desktop\\') + r' jugadores.csv',
                index=False, header=True)
fin = time.time()

m, s = divmod(fin-ini, 60)
print(f"Tiempo de ejecución: {m:.0f} minuto(s) y {s:.2f} segundo(s)")
