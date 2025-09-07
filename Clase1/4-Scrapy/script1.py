# Importaciones de Scrapy
from scrapy import Spider
from scrapy.loader import ItemLoader
from scrapy.item import Field, Item
from scrapy.selector import Selector

# Definición del item que se va a extraer
class Pregunta(Item):
    # Campos del item
    id = Field()  # Identificador de la pregunta
    pregunta = Field()  # Texto de la pregunta
    descripcion = Field()  # Descripción de la pregunta (no se utiliza)

# Definición del spider
class StackOverflowSpider(Spider):
    # Nombre del spider
    name = "MiPrimerSpider"
    
    # Configuraciones personalizadas (USER_AGENT)
    custom_settings = {
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # URL de inicio para la extracción de datos
    start_urls = ['https://stackoverflow.com/questions']

    # Método de parseo de la página web
    def parse(self, response):
        # Selector de la página web
        sel = Selector(response)
        
        # Selección de las preguntas en la página
        preguntas = sel.xpath('//div[@id="questions"]/div[@data-post-id]')
        
        # Contador de preguntas
        i = 0
        
        # Bucle para iterar sobre las preguntas
        for pregunta in preguntas:
            # Cargador de datos para la pregunta
            item = ItemLoader(item=Pregunta(), selector=pregunta)
            
            try:
                # Extracción del texto de la pregunta
                item.add_xpath('pregunta', './/h3/a/text()')
                
                # Extracción del identificador de la pregunta
                item.add_value('id', i)

                # Extracción de la descripción de la pregunta
                item.add_xpath('descripcion', './/div[contains(@class, "s-post-summary--content-excerpt")]/text()')
                
                # Incremento del contador de preguntas
                i += 1
                
                # Devolución del item cargado con los datos
                yield item.load_item()
            except Exception as e:
                # Manejo de errores durante la extracción de datos
                print(f"Error al cargar pregunta: {e}")