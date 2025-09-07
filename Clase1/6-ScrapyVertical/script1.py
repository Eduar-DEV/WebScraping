# Importaciones de Scrapy
from scrapy import Spider
from scrapy.loader import ItemLoader
from scrapy.item import Field, Item
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader.processors import MapCompose, TakeFirst

class Hotel(Item):
    # Campos del item
    
    #id = Field()  # Identificador del hotel
    nombre = Field()  # Nombre del hotel
    precio = Field()  # Precio del hotel
    direccion = Field()  # Dirección del hotel
    amenities = Field()  # Servicios del hotel

class TripAdvisor(CrawlSpider):
    name = "Hoteles"
      # Configuraciones personalizadas (USER_AGENT)
    custom_settings = {
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cookie': 'cookies=accept'
    }
    allowed_domains = ["www.tripadvisor.cl"]
    start_urls = ["https://www.tripadvisor.cl/Hotels-g294232-Japan-Hotels.html"]
    download_delay = 2

    rules = (
        Rule(
            LinkExtractor(
                allow=("/Hotel_Review-",)), callback="parse_hotel", follow=True),
    )

    def parse_hotel(self, response):
        sel = Selector(response)
        item = ItemLoader(item=Hotel(), selector=sel)
        
        #item.add_xpath("id", '//*[@id="HEADING"]/text()')
        item.add_xpath("nombre", '//h1[@id="HEADING"]/text()')
        item.add_xpath("precio", '////div[@data-automation="finalPrice"]/text()')
        item.add_xpath("direccion", '//div[contains(concat(" ", normalize-space(@class), " "), " irnhs ") and contains(concat(" ", normalize-space(@class), " "), " f ") and contains(concat(" ", normalize-space(@class), " "), " k ")]//span[contains(concat(" ", normalize-space(@class), " "), " biGQs ") and contains(concat(" ", normalize-space(@class), " "), " _P ") and contains(concat(" ", normalize-space(@class), " "), " AWdfh ")]/text()')
        item.add_xpath("amenities", '//div[contains(concat(" ", normalize-space(@class), " "), " gFttI ") and contains(concat(" ", normalize-space(@class), " "), " f ") and contains(concat(" ", normalize-space(@class), " "), " _c ")]/text()')

        yield item.load_item()