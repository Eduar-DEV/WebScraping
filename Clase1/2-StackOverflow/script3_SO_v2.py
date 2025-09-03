import requests
from bs4 import BeautifulSoup
import json   # 👈 para manejar JSON

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}   

url = "https://stackoverflow.com/questions"
respuesta = requests.get(url, headers=headers)
soup = BeautifulSoup(respuesta.text, "html.parser")

contenedor_de_preguntas = soup.find(id="questions")
lista_de_preguntas = contenedor_de_preguntas.find_all('div', class_ = "s-post-summary js-post-summary")

# Lista donde guardaremos cada pregunta
preguntas_json = []

for pregunta in lista_de_preguntas:
    elemento_texto_pregunta = pregunta.find('h3')
    texto_pregunta = elemento_texto_pregunta.text.strip()


    descripcion_pregunta = elemento_texto_pregunta.find_next_sibling('div').text
 
    descripcion_pregunta = descripcion_pregunta.replace("\n", " ").replace("\r", " ").strip()
    
    preguntas_json.append({
        "titulo": texto_pregunta,
        "descripcion": descripcion_pregunta
    })

# Guardar en archivo JSON con indentación bonita
with open("Ejemplos_JSON/preguntas2.json", "w", encoding="utf-8") as f:
    json.dump(preguntas_json, f, ensure_ascii=False, indent=4)

print("✅ Archivo 'preguntas.json' creado con éxito")
