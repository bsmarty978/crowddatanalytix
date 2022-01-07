import json
from ast import literal_eval

from extruct import JsonLdExtractor
from itemloaders.processors import Compose
from itemloaders.processors import SelectJmes as pick
from jmespath import search
from scrapy import Spider
from scrapy.http import Request, Response
from w3lib.html import remove_tags, replace_entities, replace_escape_chars
from w3lib.url import add_or_replace_parameter, url_query_cleaner, url_query_parameter

# from materialbank.items import ProductLoader
# from materialbank.utils.format import formatter

from items import ProductLoader
# from materialbank.utils.format import formatter


class CamirafabricsSpider(Spider):
    name = "camirafabrics"
    allowed_domains = ["camirafabrics.com"]
    start_urls = [
        "https://www.camirafabrics.com/api/category-results/contract?page=1",
        "https://www.camirafabrics.com/api/category-results/buscoach?page=1",
    ]

    custom_settings = {"SPLITVARIANTS_ENABLED": True}

    def parse(self, response: Response, **kwargs):
        response_data = json.loads(s=literal_eval(response.text))

        items = response_data["items"]
        for item in items:
            product_url = response.urljoin(url=item["url"])
            yield Request(url=product_url, callback=self.parse_item)

        # Pagination
        current_page = int(url_query_parameter(url=response.url, parameter="page"))
        total_num_of_pages = response_data["pagination"]["pageCount"]
        if current_page < total_num_of_pages:
            page_num = current_page
            page_num += 1
            next_page = add_or_replace_parameter(
                url=response.url, name="page", new_value=page_num
            )
            yield Request(url=next_page)

    def parse_item(self, response: Response, **kwargs):
        il = ProductLoader(response=response)
        # Parse product variants
        variants = self.parse_variants(response=response)
        il.add_value("variants", variants)
        # Parse specs
        specifications = self.parse_specifications(response=response)
        il.add_value("specifications", specifications)

        jslde = JsonLdExtractor()
        json_ld_data = jslde.extract(htmlstring=response.text)

        il.add_value("name", json_ld_data, pick('[?"@type" == `Product`].name | [0]'))
        il.add_value(
            "description",
            json_ld_data,
            pick('[?"@type" == `Product`].description | [0]'),
            Compose(remove_tags, replace_escape_chars, replace_entities),
        )
        il.add_value("brand", json_ld_data, pick('[?"@type" == `Product`].brand | [0]'))
        il.add_value(
            "image_urls", json_ld_data, pick('[?"@type" == `Product`].image.url | [0]')
        )

        images = search(
            expression='[?"@type" == `ImageGallery`].associatedMedia | [].url',
            data=json_ld_data,
        )
        il.replace_value(
            "image_urls", il.get_collected_values("image_urls").extend(images)
        )

        il.add_xpath(
            "file_urls",
            '//section[@class="specification__section"]//h6[contains(normalize-space(text()), "Documents")]/following-sibling::ul/li/a/@href',
        )
        il.replace_value(
            "file_urls",
            [
                response.urljoin(url=file_url)
                for file_url in il.get_collected_values("file_urls")
            ],
        )

        yield il.load_item()

    def parse_variants(self, response: Response, **kwargs):
        variants = []

        product_colourways = response.css("#productColourways").attrib[
            "data-dc-colourways-options"
        ]
        colourways = json.loads(s=product_colourways).get("colourways")

        for colourway in colourways:
            variant = {}
            variant["sku"] = colourway["sku"]
            variant["colour"] = colourway["title"]

            image = colourway["image"].split(",")[0]
            variant["main_image"] = response.urljoin(url=url_query_cleaner(url=image))
            variants.append(variant)

        return variants

    # @formatter
    def parse_specifications(self, response: Response, **kwargs):
        specs = {}

        for item in response.css(".specification__row .specification__content-row"):
            key = item.css(".specification__content-title::text").get("").strip()
            values = item.css(
                ".specification__content-data ::text, .specification__content-data-item ::text"
            ).getall()
            values = filter(None, [value.strip() for value in values])
            specs[key] = ",".join(values)

        return specs
