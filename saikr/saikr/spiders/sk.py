import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from saikr.items import SaikrItem


def data_format(content):
    if content is None or content.find('— —') != -1:
        content = '暂未公布'
    return content.strip()


class SkSpider(CrawlSpider):
    name = 'sk'
    allowed_domains = ['www.saikr.com']
    start_urls = ['https://www.saikr.com/vs']

    rules = (
        Rule(LinkExtractor(allow=r'page=\d+$'), callback='parse_page', follow=True),
    )

    x_type = []

    def parse_page(self, response):
        li_list = response.xpath("//ul[@class='list']/li")
        for li in li_list:
            href = li.xpath("./div/h3/a/@href").extract_first()
            yield scrapy.Request(url=href, callback=self.parse_contest)

    def parse_contest(self, response):
        name = response.xpath("//div[@id='eventDetailBox']/h1/text()").extract_first()
        organizer_list = response.xpath("//h3[contains(text(),'主办方')]/../..//ul/li")
        organizers = ''
        for i in range(len(organizer_list)):
            o = organizer_list[i].xpath("./div/text()").extract_first().strip()
            if i < len(organizer_list) - 1:
                organizers += o + ', '
            else:
                organizers += o
        register_time = response.xpath("//h3[contains(text(),'报名时间')]/../..//ul/li/div/text()").extract_first()
        contest_time = response.xpath("//h3[contains(text(),'比赛时间')]/../..//ul/li/div/text()").extract_first()
        type_list = response.xpath("//h3[contains(text(),'竞赛类别')]/../..//ul/li/div/span")
        types = ''
        for i in range(len(type_list)):
            t = type_list[i].xpath("./text()").extract_first().strip().replace('&', ', ')
            self.x_type.extend(t.split(','))
            if i < len(type_list) - 1:
                types += t + ', '
            else:
                types += t
        item = SaikrItem()
        item['name'] = data_format(name)
        item['organizers'] = data_format(organizers)
        item['register_time'] = data_format(register_time)
        item['contest_time'] = data_format(contest_time)
        item['types'] = data_format(types)
        item['url'] = response.url
        yield item
