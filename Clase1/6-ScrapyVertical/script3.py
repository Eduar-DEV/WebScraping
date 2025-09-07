from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.item import Field, Item
from scrapy import Selector, Request
from scrapy.loader.processors import MapCompose, TakeFirst

class Hotel(Item):
    nombre = Field()
    precio = Field()
    direccion = Field()
    amenities = Field()

class TripAdvisor(CrawlSpider):
    name = "Hoteles"
    allowed_domains = ["tripadvisor.cl"]
    start_urls = ["https://www.tripadvisor.cl/Hotels-g294232-Japan-Hotels.html"]
    download_delay = 2
    custom_settings = {
        "USER_AGENT": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "AUTOTHROTTLE_ENABLED": True,
        "RETRY_TIMES": 2,
        "RETRY_HTTP_CODES": [403, 429, 500, 502, 503, 504],
        # Para inspeccionar 403 en parse_hotel
        "HTTPERROR_ALLOWED_CODES": [403],
    }

    rules = (
        Rule(
            LinkExtractor(allow=(r"/Hotel_Review-")),
            callback="parse_hotel",
            follow=True
        ),
    )

    def quitarSimboloDolar(self, value):
        return value.replace("$", "").replace(".", "").strip()

    def parse_hotel(self, response):
        # Si te siguen llegando 403, verás aquí la página de bloqueo
        sel = Selector(response)
        loader = ItemLoader(item=Hotel(), selector=sel)

        # Estos selectores probablemente NO funcionen por cambios de TripAdvisor.
        # Úsalos solo como placeholder hasta que inspecciones el DOM real.
        loader.add_xpath("nombre", "//h1[@id='HEADING']/text()")
        loader.add_xpath("precio", "//div[@data-automation='finalPrice']/text()", MapCompose(self.quitarSimboloDolar))
        loader.add_xpath("direccion", '//div[contains(concat(" ", normalize-space(@class), " "), " irnhs ") and contains(concat(" ", normalize-space(@class), " "), " f ") and contains(concat(" ", normalize-space(@class), " "), " k ")]//span[contains(concat(" ", normalize-space(@class), " "), " biGQs ") and contains(concat(" ", normalize-space(@class), " "), " _P ") and contains(concat(" ", normalize-space(@class), " "), " AWdfh ")]/text()')
        loader.add_xpath("amenities", '//div[contains(@class, "gFttI") and contains(@class, "_c")]//div[@data-test-target="amenity_text"]//text()')

        yield loader.load_item()
