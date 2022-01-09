#NOTE: This spider is created Using ItemLoader


import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin
from canddspider.items import Product

class CanddspySpider(CrawlSpider):
    name = 'canddspy'
    allowed_domains = ['colouranddesign.com']
    user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Mobile Safari/537.36'

    def start_requests(self):
        # yield scrapy.Request(url='https://siege.gg/matches?tab=results')
        yield scrapy.Request(url='https://colouranddesign.com/wallcoverings', headers={
        'User-Agent': self.user_agent
        })

    def set_user_agent(self, request):
        request.headers['User-Agent']=self.user_agent
        return request

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//ul[@id="products-grid"]/li//div[@class="product_thumbnail "]/a'), callback='parse_item', follow=True), #for every match
        Rule(LinkExtractor(restrict_xpaths='//a[@class="next page-numbers"]')),    #for next page
    )

    def parse_item(self, response):
        item = Product()

        name = response.xpath('//h1[@class="product_title entry-title"]/text()').get()
        sku = response.xpath('//div[@class="sku"]/text()').get()
        colorName = response.xpath('//div[@class="colorName"]/text()').get()
        img_urls = response.xpath('//div[@class="product_images"]//img/@src').getall()

        specs = []
        spec_data = response.xpath('(//table)[1]//tr')
        conditions = len(response.xpath('(//table)[2]//tr'))
        if conditions > 0:
            # file_data = response.xpath('(//table)[2]//tr//a/@href').getall()
            file_data = [urljoin(base='https://colouranddesign.com',url=i) for i in response.xpath('//div[@id="tab-document_tab"]//a/@href').getall()]


            for spec in spec_data:
                specs.append(
                    {
                        "name" : spec.xpath('.//th/text()').get(),
                        "value": spec.xpath('.//td/p/text()').get()
                    }
                )
        else:
            descp = response.xpath('//div[@id="tab-description"]//p/text()').getall()
            for i in descp:
                d = i.split(':')
                if len(d) == 2:
                    specs.append(
                        { 
                            "name" : d[0],
                            "value": d[1]
                        }
                    )
                else:
                    specs.append({"name":'description', "value": d})
            # file_data = response.xpath('//div[@id="tab-document_tab"]//a/@href').getall()
            file_data = [urljoin(base='https://colouranddesign.com',url=i) for i in response.xpath('//div[@id="tab-document_tab"]//a/@href').getall()]
        
        item["name"] = name
        item["sku"] = sku
        item["colour"] = colorName
        item["specifications"]=specs
        item["file_urls"] = file_data
        item["image_urls"] = img_urls       

        yield item 
