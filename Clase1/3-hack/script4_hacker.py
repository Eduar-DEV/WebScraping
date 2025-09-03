import requests
from bs4 import BeautifulSoup
import json


url = "https://news.ycombinator.com"
url_base = "https://news.ycombinator.com"  # Define la variable url_base

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}   

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser") # se Carga el contenido HTML
with open('arbol_html.json', 'w') as archivo:
    json.dump(soup.prettify(), archivo)

lista_Noticias = soup.find_all('tr',class_="athing submission") # find_all retorna una lista

noticias_json = []

for noticia in lista_Noticias:
    titulo = noticia.find('span', class_="titleline").text # extrae el texto incluso de los hijos dentro
    enlace = noticia.find('span', class_="titleline").find('a')['href'] # extrae el enlace

    metadata = noticia.find_next_sibling()

    score =0
    comentarios = 0

    try: # habian datos nulos -> al extraer texto de datos nulos, el codigo se rompe.
        score_tmp = metadata.find('span', class_="score").text
        score_tmp = score_tmp.replace(' points', '').strip()
        score = int(score_tmp) if score_tmp.isdigit() else 0
    except AttributeError:
        score = 0

    try: # habian datos nulos -> al extraer texto de datos nulos, el codigo se rompe.
        comentarios_tmp = metadata.find('span', attrs={'class':'subline'}).text # otra forma de buscar con mayor flexibilidad
        comentarios_tmp = comentarios_tmp.split('|')[-1]
        comentarios_tmp = comentarios_tmp.replace(' comments', '').strip()
        comentarios = int(comentarios_tmp) if comentarios_tmp.isdigit() else 0
    except AttributeError:
        comentarios = 0

    if enlace and enlace.startswith('item'): # Verifica si el enlace en nuevo o existente, concatenado url_base con la extencion
        enlace = url_base + '/' + enlace

    noticias_json.append({
        "titulo": titulo,
        "enlace": enlace,
        "metadata": {
            "score": score,
            "comentarios": comentarios
        }
    })

with open("noticias.json", "w", encoding="utf-8") as f:
    json.dump(noticias_json, f, ensure_ascii=False, indent=4)

print("✅ Archivo 'noticias.json' creado con éxito")