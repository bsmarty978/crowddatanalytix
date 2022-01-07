import json
import re
from urllib.parse import unquote, urljoin

from itemloaders.processors import SelectJmes as pick
from scrapy.http import Request, Response
from scrapy.item import Field
from scrapy.spiders import Spider
from w3lib.url import add_or_replace_parameter

from items import Product, ProductLoader
# import formatter


class MohawkItem(Product):
    color_number = Field()


class MohawkLoader(ProductLoader):
    default_item_class = MohawkItem


class MohawkgroupSpider(Spider):
    name = "mohawkgroup"
    allowed_domains = ["mohawkgroup.com"]
    start_urls = ["https://www.mohawkgroup.com/api/product/suggestStyles"]

    custom_settings = {
        "SPLITVARIANTS_ENABLED": True,
    }

    def parse(self, response: Response, **kwargs):
        response_data = json.loads(s=response.text)

        for item in response_data:
            product_url = urljoin(base=response.url, url=item["path"])
            yield Request(url=product_url, callback=self.parse_item)

    def parse_item(self, response: Response, **kwargs):
        jscode = response.xpath("//script[contains(., 'initData')]/text()").get()
        json_string = None

        regex = r"initData\s?=\s?(.+);$"
        matches = re.finditer(regex, jscode, re.MULTILINE)
        for match in matches:
            for group in match.groups():
                if group:
                    json_string = group
                    break

        response_data = json.loads(s=json_string)

        il = MohawkLoader()
        # Parse specs
        specifications = self.parse_specifications(response=response_data)
        il.add_value("specifications", specifications)
        # Parse variants
        style_number = il.get_value(
            response_data, pick("productSpecifications.style.styleNumber")
        )
        colour_variants = il.get_value(
            response_data,
            pick(
                "productSpecifications.style.colors[*].{colour: colorName, color_number: colorNumber, main_image: swatchPath}"
            ),
        )
        variants = []
        for variant in colour_variants:
            variant["sku"] = "‐".join([style_number, variant["color_number"]])
            variant["main_image"] = unquote(
                add_or_replace_parameter(
                    url=variant["main_image"],
                    name="$mgpdpswatchrectangle$",
                    new_value="",
                )
            )
            variants.append(variant)

        il.add_value("variants", variants)

        il.add_value(
            "name", response_data, pick("productSpecifications.style.styleName")
        )
        il.add_value(
            "file_urls",
            response_data,
            pick("productSpecifications.style.documents | values(@) | [].path"),
        )
        il.add_value(
            "image_urls",
            response_data,
            pick("productSpecifications.style.images | values(@) | [].path"),
        )
        il.add_value(
            "breadcrumbs",
            response_data,
            pick("productSpecifications.style.[productFamily, productSubFamily]"),
        )
        yield il.load_item()

    # @formatter
    def parse_specifications(self, response: dict, **kwargs):
        specifications = {}
        spec_types = ["designSpecifications", "sustainabilitySpecifications"]
        for spec_type in spec_types:
            spec = response["productSpecifications"][spec_type]
            for spec_key, spec_dictionary in spec.items():
                key = spec_dictionary["name"]
                value = spec_dictionary["value"]
                specifications[key] = value
        return specifications
