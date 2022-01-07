# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from itemloaders.processors import Identity, Join, MapCompose, TakeFirst
from scrapy.item import Field, Item
from scrapy.loader import ItemLoader


class BaseItemLoader(ItemLoader):
    def add_fallback_css(self, field_name, css, *processors, **kw):
        if any(self.get_collected_values(field_name)):
            return
        self.add_css(field_name, css, *processors, **kw)

    def add_fallback_xpath(self, field_name, xpath, *processors, **kw):
        if any(self.get_collected_values(field_name)):
            return
        self.add_xpath(field_name, xpath, *processors, **kw)


class Product(Item):
    # Magic fields
    job_id = Field()
    job_time = Field()
    timestamp = Field()
    spider = Field()
    url = Field()
    # Scrapy fields
    file_urls = Field()
    files = Field()
    image_urls = Field()
    images = Field()
    # Regular fields
    sku = Field()
    name = Field()
    brand = Field()
    colour = Field()
    breadcrumbs = Field()
    main_image = Field()
    description = Field()
    specifications = Field()
    product_variants = Field()
    # Special fields
    variants = Field()


class ProductLoader(BaseItemLoader):
    default_item_class = Product
    default_output_processor = TakeFirst()
    # Field-specific processors
    colour_in = MapCompose(str.strip)
    breadcrumbs_out = Identity()
    description_in = MapCompose(str.strip)
    description_out = Join()
    specifications_out = Identity()
    file_urls_out = Identity()
    image_urls_out = Identity()
    product_variants_out = Identity()
    variants_out = Identity()
