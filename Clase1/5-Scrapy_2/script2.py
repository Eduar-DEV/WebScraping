# Importaciones de Scrapy
from scrapy import Spider
from scrapy.loader import ItemLoader
from scrapy.item import Field, Item
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess



class Noticia(Item):
    # Campos del item
    id = Field()  # Identificador de la noticia
    titular = Field()  # Título de la noticia
    descripcion = Field()  # Descripción de la noticia

class ElUniverso(Spider):
    name = "MiSegundoSpider"
    
    # Configuraciones personalizadas (USER_AGENT)
    custom_settings = {
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    start_urls = ['https://www.eluniverso.com/deportes/']


    def parse(self, response):
        # Lógica de extracción de datos
        soup = BeautifulSoup(response.text, 'html.parser')
        contenedor_noticias = soup.find_all('section', class_='px-2')

        for contenedor in contenedor_noticias:
            noticias = contenedor.find_all('li', class_='relative')
            for noticia in noticias:
                item = ItemLoader(Noticia(), response.body)
                try:
                    item.add_value('id', noticias.index(noticia))
                    item.add_value('titular', noticia.find('h2').get_text(strip=True) if noticia.find('h2') else 'N/A')
                    item.add_value('descripcion', noticia.find('p').get_text(strip=True) if noticia.find('p') else 'N/A')
                    yield item.load_item()
                except Exception as e:
                    self.logger.error(f"Error procesando noticia: {e}")

process = CrawlerProcess({
    'FEED_FORMAT': 'json',
    'FEED_URI': 'output.json'
})

process.crawl(ElUniverso)
process.start()

#Se ejecuta con: uv run script2.py