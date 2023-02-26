# librerías a usar
from collections import defaultdict
import math
import requests
import os
import time
import pandas as pd
import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ini = time.time()
ua = UserAgent()
# declaramos cabeceras aleatorias con User-Agent
headers = {"user-agent": ua.random}


def formato(date_string):
    # traducción al inglés para darle formato
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
        "diciembre": "december",
    }
    date_string = date_string.replace(
        date_string.split()[1], month_translations[date_string.split()[1]]
    )
    date_object = datetime.datetime.strptime(date_string, "%d %B %Y")
    month_number = date_object.month
    new_date_string = date_string.replace(" ", "/")
    new_date_string = new_date_string.replace(
        date_object.strftime("%B"), f"{month_number:02}"
    )
    return new_date_string


# primero definimos las competiciones a scrapear (para concatenar luego en el URL)


def elegir_competicion(nombres_competiciones):
    while True:
        print("Lista de competiciones disponibles:")
        for i, nombre in enumerate(nombres_competiciones):
            print(f"{i}. {nombre}")
        try:
            competicion_elegida = int(
                input(
                    "Elija una competición tecleando un número (0-{}): ".format(
                        len(nombres_competiciones) - 1
                    )
                )
            )
            if 0 <= competicion_elegida <= len(nombres_competiciones) - 1:
                return competicion_elegida
            else:
                print("Por favor elija un número dentro del rango")
        except ValueError:
            print("Por favor introduce un número")


def elegir_grupo(nombres_grupos_nac):
    while True:
        print("Grupos disponibles:")
        for i, nombre in enumerate(nombres_grupos_nac):
            print(f"{i}. {nombre}")
        try:
            grupo_elegido = int(
                input(
                    "Elija una competición tecleando un número (0-{}): ".format(
                        len(nombres_grupos_nac) - 1
                    )
                )
            )
            if 0 <= grupo_elegido <= len(nombres_grupos_nac) - 1:
                return grupo_elegido
            else:
                print("Por favor elija un número dentro del rango")
        except ValueError:
            print("Por favor introduce un número")


nombres_grupos_nac = [
    "grupo1",
    "grupo2",
    "grupo3",
    "grupo4",
    "grupo5",
    "grupo6",
    "grupo7",
    "grupo8",
    "grupo9",
    "grupo10",
    "grupo11",
    "grupo12",
    "grupo13",
    "grupo14",
    "grupo15",
    "grupo16",
    "grupo17",
]
nombres_competiciones = [
    "primera",
    "segunda",
    "primera_division_rfef",
    "segunda_division_rfef",
    "tercera_division_rfef",
    "galicia",
    "liga_revelacao",
    "vitalis",
    "portugal",
    "nacional_juvenil",
    "division_honor_juvenil",
]
competicion_elegida = elegir_competicion(nombres_competiciones)
grupo_elegido = elegir_grupo(nombres_grupos_nac)


datos_totales = []


def filtrar_columnas(diccionario):
    columnas_permitidas = {
        "URL",
        "Temporada",
        "Equipo",
        "Edad",
        "Nombre",
        "Fecha nacimiento",
        "Localidad nacimiento",
        "Demarcación",
        "Pierna predominante",
        "ELO",
        "Potencial",
        "Competición principal",
        "Equipo anterior",
        "Competición anterior",
        "Agente",
        "Fin contrato",
        "Valor mercado",
        "Salario",
        "MinutosJugados",
        "Goles",
        "Twitter",
        "Posicion principal",
        "Posicion princ %",
        "Posicion Alternativa",
        "Posicion Altern%",
    }
    keys_to_remove = []
    for key in diccionario:
        if key not in columnas_permitidas:
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del diccionario[key]
    return diccionario


# Selecciona el nombre de la competición elegida
nombre_competicion = nombres_competiciones[competicion_elegida]
nombre_grupo = nombres_grupos_nac[grupo_elegido]

# guardamos los urls de los jugadores y equipos para poder iterar sobre ellos en las consultas y más tarde meterlos en el .csv

urls_equipos = []

# en este dict guardamos los datos que no tienen las mismas etiquetas a la hora de acceder

datos = {}


redes_jugadores = []
nombres_jugadores = []
edad_jugadores = []

# recorremos las ligas
paginaCompeticiones = f"https://es.besoccer.com/competicion/clasificacion/{nombre_competicion}/2023/{nombre_grupo}"
respuestaCompeticiones = requests.get(paginaCompeticiones, headers=headers)
htmlCompeticiones = BeautifulSoup(
    respuestaCompeticiones.content, "html.parser")
nombresEquipos = htmlCompeticiones.find_all("td", {"class": "name"})

# y ahora guardamos esos enlaces a los equipos
urls_equipos = [
    equipo.find("a", href=True)["href"].replace("equipo", "equipo/plantilla")
    for equipo in nombresEquipos
    if equipo.find("span", {"class": "team-name"})
]

# una vez tenemos los equipos de la competición elegida, recorremos todos los jugadores de cada uno
session = requests.Session()

jugadores = []
equipos_rep = []
urls_jugadores = []
occurrences = defaultdict(int)

for url_equipo in urls_equipos:
    response = session.get(url_equipo, headers=headers)
    htmlEquipos = BeautifulSoup(response.text, "html.parser")
    nombre_equipo = htmlEquipos.select_one("h2.title.ta-c").text
    occurrences[nombre_equipo] += 1
    jugadores += htmlEquipos.select("td.name")
    equipos_rep += [nombre_equipo] * len(jugadores)

    urls_jugadores = [jugador.select_one(
        "a[href]")["href"] for jugador in jugadores]

    for urljugador in urls_jugadores:
        respuestaJugadores = requests.get(urljugador, headers=headers)
        htmlJugadores = BeautifulSoup(
            respuestaJugadores.content, "html.parser")

        redesJugadores = htmlJugadores.find("div", class_="desc-boxes")
        twitter_url = None
        if redesJugadores is not None:
            twitter = redesJugadores.find_all(
                "div", class_=["sub-text2", "break-url"])
            for sub, url in zip(twitter[::2], twitter[1::2]):
                if sub.text.strip() == "Twitter" and twitter != None:
                    twitter_url = url.text
                    break
        redes_jugadores.append(twitter_url)

        datos = {}
        datos["URL"] = urljugador

        main_role = htmlJugadores.find("div", class_="main-role")
        other_roles = htmlJugadores.find("ul", class_="position-list")

        if main_role:
            role_span = main_role.find_all("span")
            if role_span:
                datos["Posicion principal"] = role_span[0].text
                datos["Posicion princ %"] = role_span[1].text
        else:
            datos["Posicion principal"] = None
            datos["Posicion princ %"] = None

        if other_roles:
            other_role = other_roles.find_all("li")
            if other_role:
                for element in other_role:
                    text_split = element.text.strip().split("\n")
                    posicion = text_split[0]
                    porcentaje = text_split[1]
                    datos["Posicion Alternativa"] = posicion
                    datos["Posicion Altern%"] = porcentaje
        else:
            datos["Posicion Alternativa"] = None
            datos["Posicion Altern%"] = None

        for item_col in htmlJugadores.find_all("div", class_="item-col"):
            main_line = item_col.find("div", class_="main-line")
            other_line = item_col.find("div", class_="other-line")
            if main_line and other_line:
                other_line_texts = other_line.find_all("div")
                for other_line_text in other_line_texts:
                    text = other_line_text.text.strip()
                    if text == "Minutos":
                        datos["MinutosJugados"] = main_line.text.replace(
                            "'", "")
                    elif text == "Goles/90'":
                        datos["Goles"] = main_line.text

        divDataPanelTitle = htmlJugadores.find_all(
            "div", class_="panel-subtitle")

        for div in divDataPanelTitle:
            if div.text not in nombres_jugadores:
                nombres_jugadores.append(div.text)
                break
        divDataTableList = htmlJugadores.find_all("div", class_="table-row")

        for div in divDataTableList:
            divText = div.find("div")
            if divText is not None:
                continue
            for elements in divText.next_siblings:
                if elements.isspace() or divText.text == "":
                    continue
                if divText.text.strip() == "Fecha nacimiento":
                    fecha_nacimiento = datetime.datetime.strptime(
                        elements.text.strip(), "%d/%m/%Y"
                    )
                    hoy = datetime.datetime.now()
                    edad = (
                        hoy.year
                        - fecha_nacimiento.year
                        - (
                            (hoy.month, hoy.day)
                            < (fecha_nacimiento.month, fecha_nacimiento.day)
                        )
                    )
                else:
                    datos[divText.text.strip()] = elements.text.strip()
                    link = elements.find("a", class_="image-row link")
                    if link is not None:
                        datos[link.text] = link["href"]
                break
        if "Fecha nacimiento" in datos and datos["Fecha nacimiento"] != "":
            fe_nac = datetime.datetime.strptime(
                formato(datos["Fecha nacimiento"]), "%d/%B/%Y"
            )
            edad = math.trunc((datetime.datetime.now() - fe_nac).days / 365)
        else:
            edad = None

        edad_jugadores.append(edad)

        min_length = min(
            len(edad_jugadores),
            len(equipos_rep),
            len(nombres_jugadores),
            len(redes_jugadores),
        )
        for i in range(min_length):

            datos.update(
                {
                    "Edad": str(edad_jugadores[i]),
                    "Temporada": "2022/23",
                    "Equipo": equipos_rep[i],
                    "Nombre": nombres_jugadores[i],
                    "Twitter": redes_jugadores[i],
                }
            )

        filtrar_columnas(datos)
        datos_totales.append(datos)
    df = pd.DataFrame(datos_totales)
columnas_nuevas = [
    "URL",
    "Temporada",
    "Equipo",
    "Edad",
    "Nombre",
    "Fecha nacimiento",
    "Lugar nacimiento",
    "demarcacion",
    "pierna",
    "elo",
    "potencial",
    "Competicion",
    "Competicion anterior",
    "Equipo anterior",
    "Fin de Contrato",
    "Valor de Mercado",
    "Goles",
    "MinutosJugados",
    "Agente",
    "Salario",
    "Twitter",
    "Posicion principal",
    "Posicion princ %",
    "Posicion Alternativa",
    "Posicion Altern%",
]

nuevos_nombres = {
    "Localidad nacimiento": "Lugar nacimiento",
    "Demarcación": "demarcacion",
    "Pierna predominante": "pierna",
    "ELO": "elo",
    "Potencial": "potencial",
    "Competición principal": "Competicion",
    "Competición anterior": "Competicion anterior",
    "Fin contrato": "Fin de Contrato",
    "Valor mercado": "Valor de Mercado",
}

df = df.reindex(columns=columnas_nuevas)
df.rename(columns=nuevos_nombres, inplace=True)


print(df)
# exportamos a csv
df.to_csv(
    os.path.expanduser("~/Desktop\\")
    + "España-"
    + nombre_competicion
    + " - "
    + nombre_grupo
    + ".csv",
    index=False,
    header=True,
)

fin = time.time()

m, s = divmod(fin - ini, 60)
print(f"Tiempo de ejecución: {m:.0f} minuto(s) y {s:.2f} segundo(s)")
