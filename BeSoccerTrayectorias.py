from typing import Dict, Tuple, Optional, Union, List
import pandas as pd
from itertools import groupby
from collections import defaultdict
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
    while True:
        print("Lista de competiciones disponibles:")
        for i, nombre in enumerate(nombres_competiciones):
            print(f"{i}. {nombre}")
        try:
            competicion_elegida = int(input(
                "Elija una competición tecleando un número (0-{}): ".format(len(nombres_competiciones) - 1)))
            if 0 <= competicion_elegida <= len(nombres_competiciones) - 1:
                return competicion_elegida
            else:
                print("Por favor elija un número dentro del rango")
        except ValueError:
            print("Por favor introduce un número")


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

datos: Dict[str, Tuple[Optional[str], int]] = {}
equipo_actual: Optional[str] = None
jugador_actual: Optional[str] = None
total_pj: int = 0

for url in urls_trayectorias:
    html_trayectoria = BeautifulSoup(requests.get(
        url, headers=headers).content, 'html.parser')
    equipo = html_trayectoria.find(
        "a", {"class": "shield"}).find_all('span')[0].text
    pj_carrera = int(html_trayectoria.find('td', {'data-content-tab': 'tprc1'}).text) if html_trayectoria.find(
        'td', {'data-content-tab': 'tprc1'}).text.isdigit() else 0
    datos[url] = {'url:': url, 'Equipo Carrera': equipo,
                  'Pj Carrera': pj_carrera}
    if equipo_actual is None or equipo_actual != equipo:
        if jugador_actual is not None:
            datos[jugador_actual] = (equipo_actual, total_pj)
            datos[url] = (equipo_actual, total_pj)
        equipo_actual = equipo
        jugador_actual = url
        total_pj = pj_carrera
    else:
        total_pj += pj_carrera
    if url == urls_trayectorias[-1] or urls_trayectorias[urls_trayectorias.index(url) + 1].split('/')[5] != url.split('/')[5]:
        datos[jugador_actual] = (equipo_actual, total_pj)
        datos[url] = (equipo_actual, total_pj)
        datos[f'{url}_row'] = (url, None, total_pj)

datos = {k: v for k, v in datos.items() if v[1] > 0}
datos = {k: (v[0] if v else None, v[1]) for k, v in datos.items()}
datos = {k: (v[0] if v else None, v[1]) for k, v in datos.items()}

df = pd.DataFrame.from_dict(datos)
df.to_csv(os.path.expanduser('~/Desktop\\') +
          nombre_competicion + "_trayectoria.csv", index=False, header=True)
fin = time.time()

m, s = divmod(fin-ini, 60)
print(f"Tiempo de ejecución: {m:.0f} minuto(s) y {s:.2f} segundo(s)")
