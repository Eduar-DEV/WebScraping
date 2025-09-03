import requests
import lxml.html as html

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
URL = "https://es.wikipedia.org/wiki/Wikipedia:Portada"

r = requests.get(URL, headers=HEADERS, timeout=15)
r.raise_for_status()  # lanza excepción si no fue 200 OK

tree = html.fromstring(r.content)  # usar bytes evita problemas de encoding
#lis = tree.xpath('//div[@id="main-cur"]//ul/li')

#articulos = [li.xpath('normalize-space(string(.))') for li in lis if li.xpath('normalize-space(string(.))')]

#for i in articulos:   
 #   print(i)

articulos = tree.find_class('main-cur')

print(articulos[0].text_content())