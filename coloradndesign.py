import json
import re
from urllib.parse import unquote, urljoin

from itemloaders.processors import SelectJmes as pick
from scrapy.http import Request, Response
from scrapy.item import Field
from scrapy.spiders import Spider
from w3lib.url import add_or_replace_parameter

from items import Product, ProductLoader

# from materialbank.items import ProductLoader
# from materialbank.utils.format import formatter

from items import ProductLoader
# from materialbank.utils.format import formatter


class MohawkItem(Product):
    color_number = Field()


class MohawkLoader(ProductLoader):
    default_item_class = MohawkItem



class ColorandDesignSpider(Spider):
    name = "colordesign"
    allowed_domains = ["colouranddesign.com"]
    start_urls = [
        "https://colouranddesign.com/wallcoverings",
    ]

    custom_settings = {"SPLITVARIANTS_ENABLED": True, "FEED_EXPORT_ENCODING" : 'utf-8'}

    def parse(self, response: Response, **kwargs):
        response_data = json.loads(s=response.text)

        for item in response_data:
            name = item["slug"]
            count = item["count"]
            product_url = f'https://colouranddesign.com/wallcoverings/design/{name}'
            if count >1 :
                yield Request(url=product_url, callback=self.parse_item,meta={"name": name,"product_page":product_url})
            else:
                yield Request(url=product_url,callback=self.parse_specifications,meta={'name':name,"product_page":product_url,'variants': []})

    def parse_item(self, response: Response, **kwargs):

        name = response.meta['name']
        product_page = response.meta['product_page']
        colour_variants = response.xpath('//ul[@id="products-grid"]/li')
        producturl = colour_variants[0].xpath('(.//a)[1]/@href').get()
        variants = []
        for variant in colour_variants:
            vari={}
            vari["colorname"] = variant.xpath('.//div[@class="colorName"]/text()').get()
            vari["sku"] = variant.xpath('.//div[@class="productSKU"]/text()').get()
            vari["main_image"] = variant.xpath('.//img/@src').get()
            variants.append(vari)
        
        yield Request(url=producturl,callback=self.parse_specifications,meta={'name':name,'variants': variants,'product_page':product_page})
        
    def parse_specifications(self, response):
        name = response.meta['name']
        product_page = response.meta['product_page']
        variants = response.meta['variants']
        specs = {}


        spec_data = response.xpath('(//table)[1]//tr')
        n = len(spec_data)
        conditions = len(response.xpath('(//table)[2]//tr'))
        if conditions > 0:
            file_data = response.xpath('(//table)[2]//tr//a/@href').getall()
    
            for i in range(1,n):
                specs[spec_data[i].xpath('.//th/text()').get()] = spec_data[i].xpath('.//td/p/text()').get()
        else:
            descp = response.xpath('//div[@id="tab-description"]//p/text()').getall()
            for i in descp:
                d = i.split(':')
                if len(d) == 2:
                    specs[d[0]] = d[1]
                else:
                    specs['description'] = d
            file_data = [urljoin(base='https://colouranddesign.com',url=i) for i in response.xpath('//div[@id="tab-document_tab"]//a/@href').getall()]

        
        yield{
            'name' : name,
            'product_page' : product_page,
            'variants': variants,
            'Specification' : specs,
            'file_urls' : file_data    
        }
        


        #----------------#
    #     jscode = response.xpath("//script[contains(., 'initData')]/text()").get()
    #     json_string = None

    #     regex = r"initData\s?=\s?(.+);$"
    #     matches = re.finditer(regex, jscode, re.MULTILINE)
    #     for match in matches:
    #         for group in match.groups():
    #             if group:
    #                 json_string = group
    #                 break

    #     response_data = json.loads(s=json_string)

    #     il = MohawkLoader()
    #     # Parse specs
    #     specifications = self.parse_specifications(response=response_data)
    #     il.add_value("specifications", specifications)
    #     # Parse variants
    #     style_number = il.get_value(
    #         response_data, pick("productSpecifications.style.styleNumber")
    #     )
    #     colour_variants = il.get_value(
    #         response_data,
    #         pick(
    #             "productSpecifications.style.colors[*].{colour: colorName, color_number: colorNumber, main_image: swatchPath}"
    #         ),
    #     )
    #     variants = []
    #     for variant in colour_variants:
    #         variant["sku"] = "‐".join([style_number, variant["color_number"]])
    #         variant["main_image"] = unquote(
    #             add_or_replace_parameter(
    #                 url=variant["main_image"],
    #                 name="$mgpdpswatchrectangle$",
    #                 new_value="",
    #             )
    #         )
    #         variants.append(variant)

    #     il.add_value("variants", variants)

    #     il.add_value(
    #         "name", response_data, pick("productSpecifications.style.styleName")
    #     )
    #     il.add_value(
    #         "file_urls",
    #         response_data,
    #         pick("productSpecifications.style.documents | values(@) | [].path"),
    #     )
    #     il.add_value(
    #         "image_urls",
    #         response_data,
    #         pick("productSpecifications.style.images | values(@) | [].path"),
    #     )
    #     il.add_value(
    #         "breadcrumbs",
    #         response_data,
    #         pick("productSpecifications.style.[productFamily, productSubFamily]"),
    #     )
    #     yield il.load_item()

    # # @formatter
    # def parse_specifications(self, response: dict, **kwargs):
    #     specifications = {}
    #     spec_types = ["designSpecifications", "sustainabilitySpecifications"]
    #     for spec_type in spec_types:
    #         spec = response["productSpecifications"][spec_type]
    #         for spec_key, spec_dictionary in spec.items():
    #             key = spec_dictionary["name"]
    #             value = spec_dictionary["value"]
    #             specifications[key] = value
    #     return specifications
