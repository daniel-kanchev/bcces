import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bcces.items import Article


class BccesSpider(scrapy.Spider):
    name = 'bcces'
    start_urls = ['https://www.bcc.es/es/informacion-corporativa/sala-de-prensa/']

    def parse(self, response):
        links = response.xpath('//div[@class="sidebar-module"]/ul/li/a[not(@title="Galería multimedia")]/@href').getall()
        yield from response.follow_all(links, self.parse_year)

    def parse_year(self, response):
        links = response.xpath('//h3/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="bloque-contenido-meta"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="bloque-contenido"]/*[not(@class="breadcrumb")]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
