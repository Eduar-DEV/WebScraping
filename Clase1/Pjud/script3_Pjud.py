import requests
from bs4 import BeautifulSoup
import json   # 👈 para manejar JSON

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}   

url = "https://juris.pjud.cl/busqueda?Corte_Suprema"
respuesta = requests.get(url, headers=headers)
soup = BeautifulSoup(respuesta.text, "html.parser")

sentencias = soup.find(id="capa_resultados_busqueda_sentencias")
lista_sentencias = sentencias.find_all('div', style="display: inline-block; width: calc(100% - 40px);")

# Lista donde guardaremos cada pregunta
sentencias_json = []

for sentencia in lista_sentencias:
    elemento_texto_sentencia = sentencia.find('span').text.strip()
    rol_descripcion_sentencia = sentencia.find('span', style="cursor: pointer;")

    
    sentencias_json.append({
        "titulo": elemento_texto_sentencia,
        "rol": rol_descripcion_sentencia
    })

# Guardar en archivo JSON con indentación bonita
with open("Ejemplos_JSON/preguntas_test.json", "w", encoding="utf-8") as f:
    json.dump(sentencias_json, f, ensure_ascii=False, indent=4)

print("✅ Archivo 'preguntas.json' creado con éxito")
