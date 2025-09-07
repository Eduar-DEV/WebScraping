# -*- coding: utf-8 -*-
import json
from pathlib import Path
from urllib.parse import urljoin

import scrapy
from scrapy.loader import ItemLoader
from scrapy.item import Field, Item
from scrapy.selector import Selector
from scrapy_playwright.page import PageMethod


class Hotel(Item):
    nombre = Field()
    precio = Field()
    direccion = Field()
    amenities = Field()


class TripAdvisorHotelsSpider(scrapy.Spider):
    name = "Hoteles"
    allowed_domains = ["tripadvisor.cl", "www.tripadvisor.cl"]
    start_urls = ["https://www.tripadvisor.cl/"]  # precalentamiento

    # Queremos recibir 403 en el callback para inspeccionarlo
    handle_httpstatus_list = [403]

    custom_settings = {
        # Playwright
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 45000,

        # Ritmo humano
        "COOKIES_ENABLED": True,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 2.0,
        "AUTOTHROTTLE_MAX_DELAY": 8.0,
        "DOWNLOAD_DELAY": 2.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,

        # Recibir 403 y silenciar deprecation
        "HTTPERROR_ALLOWED_CODES": [403],
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",

        # UA moderno
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),

        # Opcional: configura un proxy (comenta si no tienes)
        # "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        # "PLAYWRIGHT_LAUNCH_OPTIONS": {
        #     "proxy": {"server": "http://USER:PASS@host:port"}
        # },
    }

    # Headers “de navegador” más completos
    extra_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-CL,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        # Los sec-ch-ua los suele poner Playwright, pero añadimos por si acaso:
        "sec-ch-ua": '"Chromium";v="126", "Not.A/Brand";v="24", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    hotels_list_url = "https://www.tripadvisor.cl/Hotels-g294232-Japan-Hotels.html"
    storage_state_path = "ta_state.json"  # cookies persistentes

    def start_requests(self):
        """
        1) Ir a la home para que el sitio setee cookies/consent.
        2) Luego ir a la lista de hoteles.
        """
        yield scrapy.Request(
            self.start_urls[0],
            headers=self.extra_headers,
            callback=self.goto_list,
            errback=self.errback,
            meta={
                "playwright": True,
                "playwright_context_kwargs": {
                    # Persistimos estado (cookies/localStorage) entre corridas
                    "storage_state": self._load_storage_state(),
                    "locale": "es-CL",
                    "timezone_id": "America/Santiago",
                    "user_agent": self.settings.get("USER_AGENT"),
                    # Puedes fijar viewport si quieres
                    "viewport": {"width": 1366, "height": 850},
                    # "proxy": {"server": "http://USER:PASS@host:port"},  # si lo necesitas
                    "extra_http_headers": self.extra_headers,
                },
                "playwright_include_page": True,  # para poder ejecutar acciones si quisiéramos
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "domcontentloaded"),
                    PageMethod("wait_for_timeout", 1500),
                ],
            },
            dont_filter=True,
        )

    def goto_list(self, response):
        # Guardar cookies por si la home cargó consentimiento
        self._save_storage_state(response)

        # Si la home devolvió 403, guarda el HTML para inspección
        if response.status == 403:
            self._save_debug_html(response, "home_403.html")

        # Ahora ir a la lista de hoteles
        yield scrapy.Request(
            self.hotels_list_url,
            headers={**self.extra_headers, "Referer": response.url},
            callback=self.parse_list,
            errback=self.errback,
            meta={
                "playwright": True,
                "playwright_context_kwargs": {
                    "storage_state": self._load_storage_state(),
                    "locale": "es-CL",
                    "timezone_id": "America/Santiago",
                    "user_agent": self.settings.get("USER_AGENT"),
                    "viewport": {"width": 1366, "height": 850},
                    "extra_http_headers": self.extra_headers,
                },
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "domcontentloaded"),
                    PageMethod("wait_for_timeout", 1500),
                ],
            },
        )

    def parse_list(self, response):
        self.logger.info(f"Status {response.status} | Title: {response.css('title::text').get()}")

        # Persistimos cookies cada vez que pasamos por aquí
        self._save_storage_state(response)

        if response.status == 403:
            # Guardar el HTML del bloqueo para ver qué pide el WAF
            self._save_debug_html(response, "list_403.html")
            return

        # Enlaces a hoteles
        hotel_links = response.css('a[href*="/Hotel_Review-"]::attr(href)').getall()
        for href in hotel_links:
            url = urljoin(response.url, href.split("?")[0])
            yield scrapy.Request(
                url,
                headers={**self.extra_headers, "Referer": response.url},
                callback=self.parse_hotel,
                errback=self.errback,
                meta={
                    "playwright": True,
                    "playwright_context_kwargs": {
                        "storage_state": self._load_storage_state(),
                        "locale": "es-CL",
                        "timezone_id": "America/Santiago",
                        "user_agent": self.settings.get("USER_AGENT"),
                        "viewport": {"width": 1366, "height": 850},
                        "extra_http_headers": self.extra_headers,
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "domcontentloaded"),
                        PageMethod("wait_for_timeout", 1200),
                    ],
                },
            )

        # Paginación
        next_href = response.css('a[aria-label*="Siguiente"], a[aria-label*="Next"]::attr(href)').get()
        if next_href:
            next_url = urljoin(response.url, next_href)
            yield scrapy.Request(
                next_url,
                headers={**self.extra_headers, "Referer": response.url},
                callback=self.parse_list,
                errback=self.errback,
                meta={
                    "playwright": True,
                    "playwright_context_kwargs": {
                        "storage_state": self._load_storage_state(),
                        "locale": "es-CL",
                        "timezone_id": "America/Santiago",
                        "user_agent": self.settings.get("USER_AGENT"),
                        "viewport": {"width": 1366, "height": 850},
                        "extra_http_headers": self.extra_headers,
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "domcontentloaded"),
                        PageMethod("wait_for_timeout", 1000),
                    ],
                },
            )

    def parse_hotel(self, response):
        if response.status == 403:
            self._save_debug_html(response, "hotel_403.html")
            return

        sel = Selector(response)
        item = ItemLoader(item=Hotel(), selector=sel)

        # Nombre
        name = sel.css('h1#HEADING::text').get() or sel.css('h1::text').get()
        item.add_value("nombre", name)

        # Precio (varios fallbacks)
        price = sel.css('[data-automation="finalPrice"]::text').get()
        if not price:
            price = sel.css('[data-test-target="book-button"] span::text').re_first(r"\$\s?[\d\.\,]+")
        if not price:
            price = self._jsonld_pick(response, keys=("priceRange", "offers", "price"))
        item.add_value("precio", price)

        # Dirección
        address = self._jsonld_address(response)
        if not address:
            address = sel.xpath(
                '//a[contains(@href,"/Location") or contains(@href,"/Hotel_Review-")]/following::span[contains(@class,"_S")][1]/text()'
            ).get()
        item.add_value("direccion", address)

        # Amenities
        amenities = self._jsonld_amenities(response) or sel.css('[data-test-target="amenity_text"]::text').getall()
        item.add_value("amenities", [a.strip() for a in amenities] if amenities else None)

        yield item.load_item()

    # ---------- JSON-LD helpers ----------
    def _iter_jsonld(self, response):
        for s in response.css('script[type="application/ld+json"]::text').getall():
            try:
                data = json.loads(s.strip())
                if isinstance(data, list):
                    for d in data:
                        yield d
                else:
                    yield data
            except Exception:
                continue

    def _jsonld_pick(self, response, keys=("priceRange",), types=("Hotel", "LodgingBusiness")):
        for obj in self._iter_jsonld(response):
            if isinstance(obj, dict) and obj.get("@type") in types:
                for k in keys:
                    v = obj.get(k)
                    if isinstance(v, (str, int, float)):
                        return str(v)
                    if isinstance(v, dict) and "price" in v:
                        return str(v.get("price"))
                    if isinstance(v, list):
                        for x in v:
                            if isinstance(x, (str, int, float)):
                                return str(x)
                            if isinstance(x, dict) and "price" in x:
                                return str(x.get("price"))
        return None

    def _jsonld_address(self, response):
        for obj in self._iter_jsonld(response):
            if isinstance(obj, dict) and obj.get("@type") in ("Hotel", "LodgingBusiness", "LocalBusiness"):
                addr = obj.get("address")
                if isinstance(addr, dict):
                    parts = [
                        addr.get("streetAddress"),
                        addr.get("addressLocality"),
                        addr.get("addressRegion"),
                        addr.get("postalCode"),
                        addr.get("addressCountry"),
                    ]
                    parts = [p for p in parts if p]
                    if parts:
                        return ", ".join(parts)
        return None

    def _jsonld_amenities(self, response):
        for obj in self._iter_jsonld(response):
            if isinstance(obj, dict) and obj.get("@type") in ("Hotel", "LodgingBusiness"):
                feats = obj.get("amenityFeature")
                if isinstance(feats, list):
                    names = []
                    for f in feats:
                        if isinstance(f, dict):
                            n = f.get("name") or f.get("value")
                            if n:
                                names.append(str(n))
                    if names:
                        return names
        return None

    # ---------- utilidades varias ----------
    def _save_debug_html(self, response, filename):
        Path("debug").mkdir(exist_ok=True)
        p = Path("debug") / filename
        p.write_bytes(response.body or b"")
        self.logger.warning(f"Guardado {p} (status={response.status}) para inspección.")

    def _load_storage_state(self):
        p = Path(self.storage_state_path)
        return str(p) if p.exists() else None

    def _save_storage_state(self, response):
        """
        Guarda storage_state desde el contexto Playwright para persistir cookies.
        """
        page = response.meta.get("playwright_page")
        if not page:
            return
        try:
            ctx = page.context
            state = ctx.storage_state()
            Path(self.storage_state_path).write_text(json.dumps(state))
        except Exception as e:
            self.logger.debug(f"No pude guardar storage_state: {e}")

    def errback(self, failure):
        request = failure.request
        self.logger.warning(f"Fallo en {request.url} | error={failure.value}")
