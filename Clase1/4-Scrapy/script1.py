from scrapy import Spider
from scrapy.loader import ItemLoader
from scrapy.item import Field, Item
from scrapy.selector import Selector

class Pregunta(Item):
    id = Field()
    pregunta = Field()
    #descripcion = Field()

class StackOverflowSpider(Spider):
    name = "MiPrimerSpider"
    custom_settings = {
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    start_urls = ['https://stackoverflow.com/questions']

    def parse(self, response):
        sel = Selector(response)
        preguntas = sel.xpath('//div[@id="questions"]/div[@data-post-id]')
        i =0
        for pregunta in preguntas:
            item = ItemLoader(item=Pregunta(), selector=pregunta)
            try:
                item.add_xpath('pregunta', './/h3/a/text()')
                #item.add_xpath('descripcion', './/div[contains(@class, "s-post-summary--content-excerpt")]/text()')
                item.add_value('id', i)
                i+=1
                yield item.load_item()
            except Exception as e:
                print(f"Error al cargar pregunta: {e}")