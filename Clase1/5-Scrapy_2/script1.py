# Importaciones de Scrapy
from scrapy import Spider
from scrapy.loader import ItemLoader
from scrapy.item import Field, Item
from scrapy.selector import Selector

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
        sel = Selector(response)
        noticias = sel.xpath('//section[@class="px-2"]//li[@class="relative "]')
        i = 0
        for noticia in noticias:
            item = ItemLoader(item=Noticia(), selector=noticia)
            try:
                item.add_value('id', i)
                i += 1
                item.add_xpath('titular', './/h2/a/text()')
                item.add_xpath('descripcion', './/p/text()')
                yield item.load_item()
            except Exception as e:
                self.logger.error(f"Error procesando noticia: {e}")

# se ejecuta con scrapy runspider script1.py -o script2.json