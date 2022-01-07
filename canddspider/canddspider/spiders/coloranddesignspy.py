import scrapy
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

class ColoranddesignspySpider(scrapy.Spider):
    name = 'coloranddesignspy'
    allowed_domains = ['colouranddesign.com']
    start_urls = ['https://colouranddesign.com/wp-json/wc/store/products']

    def parse(self, response):
        response_data = json.loads(response.text)
