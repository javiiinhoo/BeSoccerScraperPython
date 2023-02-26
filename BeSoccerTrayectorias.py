import pandas as pd
import requests
import os
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ini = time.time()

ua = UserAgent()

# declaramos cabeceras aleatorias con User-Agent
headers = {'user-agent': ua.random}

""" https://es.besoccer.com/jugador/trayectoria/c-ronaldo-28185 """


def elegir_competicion(nombres_competiciones):
    opciones = "\n".join(
        [f"{i}. {nombre}" for i, nombre in enumerate(nombres_competiciones)])
    while True:
        print("Lista de competiciones disponibles:")
        print(opciones)
        competicion_elegida = input(
            f"Elija una competición tecleando un número (0-{len(nombres_competiciones) - 1}): ")
        if competicion_elegida.isdigit() and 0 <= int(competicion_elegida) <= len(nombres_competiciones) - 1:
            return int(competicion_elegida)
        else:
            print("Por favor elija un número dentro del rango")


nombres_competiciones = [
    "primera", "segunda", "primera_division_rfef",
    "segunda_division_rfef", "tercera_division_rfef", "galicia",
    "liga_revelacao", "vitalis", "portugal",
    "nacional_juvenil", "division_honor_juvenil"
]

nombre_competicion = nombres_competiciones[elegir_competicion(
    nombres_competiciones)]

nombres_equipos = []
partidos_jugados = []
datos_totales = []

paginaCompeticiones = f"https://es.besoccer.com/competicion/clasificacion/{nombre_competicion}/2023"
respuestaCompeticiones = requests.get(paginaCompeticiones, headers=headers)
htmlCompeticiones = BeautifulSoup(
    respuestaCompeticiones.content, 'html.parser')
nombresEquipos = htmlCompeticiones.find_all('td', {"class": "name"})

# y ahora guardamos esos enlaces a los equipos
urls_equipos = [url.replace("equipo", "equipo/plantilla") for equipo in nombresEquipos for url in [
    equipo.find("a", href=True)["href"]] if equipo.find("span", {"class": "team-name"})]

session = requests.Session()

urls_trayectorias = [jugador.find("a", href=True)["href"].replace("jugador", "jugador/trayectoria")
                     for url_equipo in urls_equipos
                     for jugador in BeautifulSoup(session.get(url_equipo, headers=headers).content, 'html.parser').find_all("td", {"class": "name"})]

"""equipo = html_trayectoria.find(
        "a", {"class": "shield"}).find_all('span')[0].text
    pj_carrera = int(html_trayectoria.find('td', {'data-content-tab': 'tprc1'}).text) if html_trayectoria.find(
        'td', {'data-content-tab': 'tprc1'}).text.isdigit() else 0"""
# Definir una lista vacía para almacenar los datos
datos = {"url": [], "Equipo Carrera": [], "Pj Carrera": []}

# Iterar sobre cada URL en urls_trayectorias
for url in urls_trayectorias:
    # Hacer una solicitud HTTP y obtener el contenido HTML
    content = session.get(url, headers=headers).content
    soup = BeautifulSoup(content, 'html.parser')

    trajectory_divs = soup.find_all('div', {'class': 'trajectory'})

    for trajectory_div in trajectory_divs:
        h2 = trajectory_div.find('h2', text='Resumen carrera')
        if h2:
            # Accede al div que contiene el h2 que necesitas
            div = h2.parent.parent

    # Buscar todas las filas con clase "row-body color-dark" dentro del div
    rows = div.find_all("tr", {"class": "row-body color-dark"})
    celdas_grises = div.find_all("td", {"class": "grey"})

    datos_celdas_grises = []

    # Obtener los datos de las filas de datos
    for row in rows:
        datos = {}
        datos["url"] = url
        datos["Equipo Carrera"] = row.find("span").text.strip()
        datos["Pj Carrera"] = row.find("td", class_="br-left").text.strip()

        datos_totales.append(datos)

    # Obtener los datos de las celdas grises
    datos["url"] = url
    datos["Equipo Carrera"] = celdas_grises[0].text.strip()
    datos["Pj Carrera"] = celdas_grises[1].text.strip()

    datos_celdas_grises.append(datos)

    # Combinar los datos en una única lista
    datos_totales += datos_celdas_grises

df = pd.DataFrame(datos_totales)

# Exportar el DataFrame a un archivo CSV
df.to_csv(os.path.expanduser('~/Desktop\\') +
          nombre_competicion + "_trayectoria.csv", index=False, header=True)
fin = time.time()

m, s = divmod(fin-ini, 60)
print(f"Tiempo de ejecución: {m:.0f} minuto(s) y {s:.2f} segundo(s)")
